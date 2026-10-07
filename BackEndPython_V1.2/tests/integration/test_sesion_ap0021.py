from __future__ import annotations

import pytest

from src.application.services.auth_service import AuthService
from src.application.services.servicio_bloqueo_cuenta import ServicioBloqueoCuenta
from src.application.services.validador_sesion import ValidadorSesion
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.cuenta_bloqueada import CuentaBloqueada
from src.domain.exceptions.sesion_invalida import SesionInvalida
from src.infrastructure.external.in_memory_bloqueo_cuenta_repo import InMemoryBloqueoCuentaRepo
from src.infrastructure.external.in_memory_estado_credencial_repo import (
    InMemoryEstadoCredencialRepo,
)
from src.infrastructure.external.in_memory_revocacion_token_store import (
    InMemoryRevocacionTokenStore,
)
from src.infrastructure.security.jwt_handler import JWTHandler
from src.infrastructure.security.password_hasher import PasswordHasher


def _bloqueo(enabled: bool = False) -> ServicioBloqueoCuenta:
    return ServicioBloqueoCuenta(
        repo=InMemoryBloqueoCuentaRepo(),
        enabled=enabled,
        max_intentos=3,
        duracion_minutos=15,
        auto_unlock=True,
        reset_on_success=True,
        count_non_existing=False,
    )


def _validador(estado, denylist, bloqueo) -> ValidadorSesion:
    return ValidadorSesion(estado_repo=estado, denylist=denylist, bloqueo=bloqueo)


class TestEstadoCredencial:
    async def test_version_default_e_incremento(self) -> None:
        repo = InMemoryEstadoCredencialRepo()
        assert await repo.obtener_version(42) == 1
        assert await repo.incrementar_version(42) == 2
        assert await repo.obtener_version(42) == 2


class TestDenylist:
    async def test_revocar_y_consultar(self) -> None:
        d = InMemoryRevocacionTokenStore()
        assert await d.esta_revocado("j1") is False
        await d.revocar("j1", 60)
        assert await d.esta_revocado("j1") is True

    async def test_expira(self) -> None:
        d = InMemoryRevocacionTokenStore()
        await d.revocar("j1", 0)
        assert await d.esta_revocado("j1") is False


class TestValidadorSesion:
    async def test_token_valido_pasa(self) -> None:
        v = _validador(InMemoryEstadoCredencialRepo(), InMemoryRevocacionTokenStore(), _bloqueo())
        await v.validar({"sub": "1", "nombre": "juan", "tv": 1, "jti": "j1"})

    async def test_version_obsoleta_falla(self) -> None:
        estado = InMemoryEstadoCredencialRepo()
        await estado.incrementar_version(1)
        v = _validador(estado, InMemoryRevocacionTokenStore(), _bloqueo())
        with pytest.raises(SesionInvalida):
            await v.validar({"sub": "1", "nombre": "juan", "tv": 1, "jti": "j1"})

    async def test_jti_revocado_falla(self) -> None:
        deny = InMemoryRevocacionTokenStore()
        await deny.revocar("j1", 60)
        v = _validador(InMemoryEstadoCredencialRepo(), deny, _bloqueo())
        with pytest.raises(SesionInvalida):
            await v.validar({"sub": "1", "nombre": "juan", "tv": 1, "jti": "j1"})

    async def test_cuenta_bloqueada_falla(self) -> None:
        bloqueo = _bloqueo(enabled=True)
        for _ in range(3):
            await bloqueo.registrar_fallo("juan", existe=True)
        v = _validador(InMemoryEstadoCredencialRepo(), InMemoryRevocacionTokenStore(), bloqueo)
        with pytest.raises(CuentaBloqueada):
            await v.validar({"sub": "1", "nombre": "Juan", "tv": 1, "jti": "j1"})

    async def test_token_sin_tv_se_trata_como_inicial(self) -> None:
        v = _validador(InMemoryEstadoCredencialRepo(), InMemoryRevocacionTokenStore(), _bloqueo())
        await v.validar({"sub": "1", "nombre": "juan"})

    async def test_token_sin_jti_no_consulta_denylist(self) -> None:
        v = _validador(InMemoryEstadoCredencialRepo(), InMemoryRevocacionTokenStore(), _bloqueo())
        await v.validar({"sub": "1", "nombre": "juan", "tv": 1})


def _auth() -> AuthService:
    return AuthService(
        jwt_handler=JWTHandler("test-secret-key-min-32-chars-xxxxx", "HS256"),
        password_hasher=PasswordHasher(),
        jwt_expire_minutes=60,
    )


class TestGenerarTokenClaims:
    def test_token_lleva_jti_tv_auth_epoch(self) -> None:
        auth = _auth()
        u = UsuarioEntity(uid=7, nombre="7", email="x@y.co", roles=[], activo=True)
        payload = auth.verificar_token(auth.generar_token(u, token_version=5))
        assert isinstance(payload["jti"], str) and payload["jti"]
        assert payload["tv"] == 5
        assert isinstance(payload["auth_epoch"], int)

    async def test_round_trip_revocacion_por_version(self) -> None:
        auth = _auth()
        estado = InMemoryEstadoCredencialRepo()
        u = UsuarioEntity(uid=7, nombre="ana", email="x@y.co", roles=[], activo=True)
        tv = await estado.obtener_version(7)
        payload = auth.verificar_token(auth.generar_token(u, token_version=tv))
        v = _validador(estado, InMemoryRevocacionTokenStore(), _bloqueo())
        await v.validar(payload)
        await estado.incrementar_version(7)
        with pytest.raises(SesionInvalida):
            await v.validar(payload)
