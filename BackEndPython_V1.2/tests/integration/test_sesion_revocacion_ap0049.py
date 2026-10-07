"""AP-0049: invalidacion de sesion ante cambios de estado del usuario.

Cierra las brechas restantes sobre la base de AP-0021: (1) chequeo vivo de
existencia y estado del usuario en ValidadorSesion (cubre eliminacion y
deshabilitacion fuera de flujo), (2) revocacion de sesiones al emitir una
contrasena temporal por un tercero (restablecimiento admin, AP-0047), (3)
eliminacion logica de cuentas con revocacion inmediata, y (4) seleccion de
persistencia durable (SQL) de la revocacion por configuracion.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.application.services.servicio_bloqueo_cuenta import ServicioBloqueoCuenta
from src.application.services.servicio_password_temporal import ServicioPasswordTemporal
from src.application.services.validador_sesion import ValidadorSesion
from src.application.use_cases.emitir_password_temporal_use_case import (
    EmitirPasswordTemporalUseCase,
)
from src.application.use_cases.gestionar_usuarios_use_case import GestionarUsuariosUseCase
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.permiso_denegado import PermisoDenegado
from src.domain.exceptions.sesion_invalida import SesionInvalida
from src.domain.services.politica_password_temporal import PoliticaPasswordTemporal
from src.domain.value_objects.estado_usuario import EstadoUsuario
from src.domain.value_objects.origen_password_temporal import OrigenPasswordTemporal
from src.domain.value_objects.rol_usuario import RolUsuario
from src.infrastructure.config import dependencies
from src.infrastructure.config.settings import Settings
from src.infrastructure.external.in_memory_bloqueo_cuenta_repo import InMemoryBloqueoCuentaRepo
from src.infrastructure.external.in_memory_estado_credencial_repo import (
    InMemoryEstadoCredencialRepo,
)
from src.infrastructure.external.in_memory_password_temporal_repo import (
    InMemoryPasswordTemporalRepo,
)
from src.infrastructure.external.in_memory_revocacion_token_store import (
    InMemoryRevocacionTokenStore,
)
from src.infrastructure.persistence.repositories.sqlalchemy_estado_credencial_repo import (
    SQLAlchemyEstadoCredencialRepo,
)
from src.infrastructure.persistence.repositories.sqlalchemy_revocacion_token_repo import (
    SQLAlchemyRevocacionTokenRepo,
)
from src.infrastructure.security.password_hasher import PasswordHasher


def _bloqueo() -> ServicioBloqueoCuenta:
    return ServicioBloqueoCuenta(
        repo=InMemoryBloqueoCuentaRepo(),
        enabled=False,
        max_intentos=3,
        duracion_minutos=15,
        auto_unlock=True,
        reset_on_success=True,
        count_non_existing=False,
    )


class _RepoUsuarioVivo:
    """Fake del puerto UsuarioRepository limitado al chequeo vivo de AP-0049."""

    def __init__(self, activos: set[int]) -> None:
        self._activos: set[int] = activos

    async def resolver_estado(self, uid: int) -> EstadoUsuario:
        return EstadoUsuario.ACTIVO if uid in self._activos else EstadoUsuario.ELIMINADO


def _claims(uid: int = 7) -> dict[str, object]:
    return {"sub": str(uid), "nombre": "ana", "tv": 1, "jti": "j1"}


# ── (1) Chequeo vivo de existencia y estado ──


class TestChequeoVivoUsuario:
    async def test_usuario_activo_pasa(self) -> None:
        v = ValidadorSesion(
            estado_repo=InMemoryEstadoCredencialRepo(),
            denylist=InMemoryRevocacionTokenStore(),
            bloqueo=_bloqueo(),
            usuario_repo=_RepoUsuarioVivo({7}),
        )
        await v.validar(_claims(7))

    async def test_usuario_eliminado_o_inactivo_falla(self) -> None:
        v = ValidadorSesion(
            estado_repo=InMemoryEstadoCredencialRepo(),
            denylist=InMemoryRevocacionTokenStore(),
            bloqueo=_bloqueo(),
            usuario_repo=_RepoUsuarioVivo(set()),
        )
        with pytest.raises(SesionInvalida):
            await v.validar(_claims(7))

    async def test_sin_repo_omite_chequeo(self) -> None:
        # Compatibilidad AP-0021: sin usuario_repo el validador se comporta como antes.
        v = ValidadorSesion(
            estado_repo=InMemoryEstadoCredencialRepo(),
            denylist=InMemoryRevocacionTokenStore(),
            bloqueo=_bloqueo(),
        )
        await v.validar(_claims(7))


# ── (2) Restablecimiento por un tercero revoca sesiones ──


def _usuario(uid: int, roles: list[RolUsuario] | None = None, activo: bool = True) -> UsuarioEntity:
    return UsuarioEntity(
        uid=uid,
        nombre=str(uid),
        email="u" + str(uid) + "@sufi.co",
        roles=roles or [],
        activo=activo,
    )


def _uc_emitir(estado: InMemoryEstadoCredencialRepo | None) -> EmitirPasswordTemporalUseCase:
    repo_usuario = AsyncMock()
    repo_usuario.obtener_cualquiera_por_uid_async.return_value = _usuario(7)
    servicio = ServicioPasswordTemporal(
        repo=InMemoryPasswordTemporalRepo(),
        politica=PoliticaPasswordTemporal(ttl_minutos=120),
        hasher=PasswordHasher(),
    )
    return EmitirPasswordTemporalUseCase(
        servicio=servicio,
        usuario_repo=repo_usuario,
        estado_credencial=estado,
    )


class TestResetAdminRevocaSesiones:
    async def test_emitir_temporal_incrementa_token_version(self) -> None:
        estado = InMemoryEstadoCredencialRepo()
        assert await estado.obtener_version(7) == 1
        uc = _uc_emitir(estado)
        entidad, clave, usuario = await uc.ejecutar_async(
            uid_objetivo=7,
            emitida_por_uid=1,
            emitida_por_usuario="admin",
            origen=OrigenPasswordTemporal("admin"),
            motivo=None,
            ip_emision=None,
        )
        assert clave
        assert usuario.uid == 7
        # AP-0049: toda sesion viva del usuario 7 queda revocada en el acto.
        assert await estado.obtener_version(7) == 2

    async def test_emitir_sin_estado_credencial_no_falla(self) -> None:
        uc = _uc_emitir(None)
        entidad, clave, _ = await uc.ejecutar_async(
            uid_objetivo=7,
            emitida_por_uid=1,
            emitida_por_usuario="admin",
            origen=OrigenPasswordTemporal("soporte"),
            motivo="mesa de ayuda",
            ip_emision="10.0.0.1",
        )
        assert entidad.uid == 7
        assert clave


# ── (3) Eliminacion logica con revocacion ──


_ADMIN: list[RolUsuario] = [RolUsuario.ADMINISTRATOR]
_ASESOR: list[RolUsuario] = [RolUsuario.ASESOR_CONSUMO]


def _uc_eliminar(
    objetivo: UsuarioEntity | None,
    estado: InMemoryEstadoCredencialRepo | None = None,
) -> tuple[GestionarUsuariosUseCase, AsyncMock]:
    repo = AsyncMock()
    repo.obtener_cualquiera_por_uid_async.return_value = objetivo
    repo.actualizar_estado_async.return_value = None
    return GestionarUsuariosUseCase(usuario_repo=repo, estado_credencial=estado), repo


class TestEliminarUsuario:
    async def test_admin_elimina_y_revoca_sesiones(self) -> None:
        estado = InMemoryEstadoCredencialRepo()
        uc, repo = _uc_eliminar(_usuario(700, [RolUsuario.COMISIONISTA]), estado)
        resultado = await uc.eliminar_async(700, actor_uid=10, actor_roles=_ADMIN)
        assert resultado.activo is False
        repo.actualizar_estado_async.assert_awaited_once_with(700, False)
        assert await estado.obtener_version(700) == 2

    async def test_no_puede_eliminar_su_propia_cuenta(self) -> None:
        uc, repo = _uc_eliminar(_usuario(10, _ADMIN))
        with pytest.raises(ValueError, match="propia cuenta"):
            await uc.eliminar_async(10, actor_uid=10, actor_roles=_ADMIN)
        repo.actualizar_estado_async.assert_not_awaited()

    @pytest.mark.parametrize("uid_sistema", [0, 1])
    async def test_no_puede_eliminar_cuentas_del_sistema(self, uid_sistema: int) -> None:
        uc, repo = _uc_eliminar(None)
        with pytest.raises(ValueError, match="cuenta del sistema"):
            await uc.eliminar_async(uid_sistema, actor_uid=10, actor_roles=_ADMIN)
        repo.obtener_cualquiera_por_uid_async.assert_not_awaited()

    async def test_no_puede_eliminar_a_otro_administrador(self) -> None:
        uc, repo = _uc_eliminar(_usuario(20, [RolUsuario.ADMINISTRATOR]))
        with pytest.raises(ValueError, match="otro administrador"):
            await uc.eliminar_async(20, actor_uid=10, actor_roles=_ADMIN)
        repo.actualizar_estado_async.assert_not_awaited()

    async def test_actor_no_administrativo_denegado(self) -> None:
        uc, repo = _uc_eliminar(_usuario(700, [RolUsuario.COMISIONISTA]))
        with pytest.raises(PermisoDenegado):
            await uc.eliminar_async(700, actor_uid=30, actor_roles=_ASESOR)
        repo.actualizar_estado_async.assert_not_awaited()

    async def test_usuario_inexistente_lanza_lookup(self) -> None:
        uc, _ = _uc_eliminar(None)
        with pytest.raises(LookupError):
            await uc.eliminar_async(999, actor_uid=10, actor_roles=_ADMIN)


# ── (4) Seleccion de persistencia durable ──


class TestSeleccionPersistencia:
    def _con_flag(self, monkeypatch: pytest.MonkeyPatch, valor: bool) -> None:
        monkeypatch.setattr(
            dependencies,
            "get_settings",
            lambda: SimpleNamespace(sesion_persistencia_sql=valor),
        )

    def test_flag_activo_con_sesion_devuelve_sql(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._con_flag(monkeypatch, True)
        sesion = object()
        assert isinstance(
            dependencies.get_estado_credencial_repo_sesion(sesion),  # type: ignore[arg-type]
            SQLAlchemyEstadoCredencialRepo,
        )
        assert isinstance(
            dependencies.get_revocacion_token_store_sesion(sesion),  # type: ignore[arg-type]
            SQLAlchemyRevocacionTokenRepo,
        )

    def test_flag_inactivo_devuelve_memoria(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._con_flag(monkeypatch, False)
        repo = dependencies.get_estado_credencial_repo_sesion(object())  # type: ignore[arg-type]
        assert isinstance(repo, InMemoryEstadoCredencialRepo)

    def test_sin_sesion_cae_a_memoria(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._con_flag(monkeypatch, True)
        repo = dependencies.get_estado_credencial_repo_sesion(None)
        assert isinstance(repo, InMemoryEstadoCredencialRepo)


def _prod_kwargs(**ov: object) -> dict[str, object]:
    base: dict[str, object] = {
        "jwt_secret_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
        "db_password": "xxxxxxxxxxxxxxxxxxxxxxxx",
        "db_user": "app_sufi",
        "smtp_password": "",
        "email_api_password": "",
        "kms_provider": "aws",
        "kms_key_id": "kms-test-key-id",
    }
    base.update(ov)
    return base


class TestPersistenciaPorEntorno:
    def test_produccion_eleva_a_sql(self) -> None:
        s = Settings(app_env="production", **_prod_kwargs())  # type: ignore[arg-type]
        assert s.sesion_persistencia_sql is True

    def test_staging_eleva_a_sql(self) -> None:
        s = Settings(app_env="staging", **_prod_kwargs())  # type: ignore[arg-type]
        assert s.sesion_persistencia_sql is True

    def test_produccion_eleva_aunque_se_configure_false(self) -> None:
        s = Settings(
            app_env="production",
            sesion_persistencia_sql=False,
            **_prod_kwargs(),  # type: ignore[arg-type]
        )
        assert s.sesion_persistencia_sql is True

    def test_desarrollo_conserva_memoria_por_defecto(self) -> None:
        s = Settings(app_env="development", sesion_persistencia_sql=False)
        assert s.sesion_persistencia_sql is False
