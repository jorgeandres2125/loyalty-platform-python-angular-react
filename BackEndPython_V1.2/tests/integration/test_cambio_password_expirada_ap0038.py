from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.services.login_throttle_service import LoginThrottleService
from src.application.services.servicio_expiracion_password import (
    ServicioExpiracionPassword,
)
from src.application.use_cases.cambiar_password_expirada_use_case import (
    CambiarPasswordExpiradaUseCase,
)
from src.application.use_cases.login_use_case import LoginUseCase
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.credencial_en_gracia import CredencialEnGracia
from src.domain.exceptions.credencial_vencida_fuera_de_gracia import (
    CredencialVencidaFueraDeGracia,
)
from src.domain.exceptions.credencial_vigente import CredencialVigente
from src.domain.exceptions.credenciales_invalidas import CredencialesInvalidas
from src.domain.services.politica_expiracion_password import PoliticaExpiracionPassword
from src.domain.value_objects.estado_credencial import EstadoCredencial
from src.infrastructure.external.in_memory_intentos_login_store import (
    InMemoryIntentosLoginStore,
)
from src.infrastructure.external.in_memory_password_expiracion_repo import (
    InMemoryPasswordExpiracionRepo,
)

AHORA: datetime = datetime(2026, 7, 3, 12, 0, 0)


def _politica(vig: int = 90, aviso: int = 7, gracia: int = 5) -> PoliticaExpiracionPassword:
    return PoliticaExpiracionPassword(vigencia_dias=vig, aviso_dias=aviso, gracia_dias=gracia)


class TestClasificacion:
    def test_vigente(self):
        cambiado = AHORA - timedelta(days=80)  # vence en 10 dias
        info = _politica().clasificar(cambiado, AHORA)
        assert info.estado == EstadoCredencial.VIGENTE

    def test_recien_vencida_es_gracia(self):
        cambiado = AHORA - timedelta(days=90) - timedelta(hours=1)  # vencio hace 1h
        info = _politica().clasificar(cambiado, AHORA)
        assert info.estado == EstadoCredencial.EN_GRACIA
        assert info.dias_restantes_gracia == 5

    def test_vencida_dos_dias_es_gracia(self):
        cambiado = AHORA - timedelta(days=92)  # vencio hace 2 dias
        info = _politica().clasificar(cambiado, AHORA)
        assert info.estado == EstadoCredencial.EN_GRACIA
        assert info.dias_desde_vencimiento == 2
        assert info.dias_restantes_gracia == 3

    def test_ultimo_dia_de_gracia(self):
        cambiado = AHORA - timedelta(days=95)  # vencio hace 5 dias
        info = _politica().clasificar(cambiado, AHORA)
        assert info.estado == EstadoCredencial.EN_GRACIA
        assert info.dias_desde_vencimiento == 5

    def test_pasada_la_gracia(self):
        cambiado = AHORA - timedelta(days=96) - timedelta(hours=1)  # vencio hace 6 dias
        info = _politica().clasificar(cambiado, AHORA)
        assert info.estado == EstadoCredencial.FUERA_GRACIA
        assert info.dias_desde_vencimiento == 6


class _RepoQueFalla:
    async def obtener_cambiado_en(self, uid):
        raise RuntimeError("BD caida")

    async def registrar_cambio(self, uid, cuando):
        raise RuntimeError("BD caida")

    async def asegurar_baseline(self, uid, cuando):
        raise RuntimeError("BD caida")


class TestServicioEstado:
    async def test_sin_baseline_es_vigente(self):
        servicio = ServicioExpiracionPassword(
            repo=InMemoryPasswordExpiracionRepo(), politica=_politica()
        )
        info = await servicio.evaluar_estado(1, AHORA)
        assert info.estado == EstadoCredencial.VIGENTE

    async def test_en_gracia(self):
        repo = InMemoryPasswordExpiracionRepo()
        await repo.registrar_cambio(1, AHORA - timedelta(days=92))
        servicio = ServicioExpiracionPassword(repo=repo, politica=_politica())
        info = await servicio.evaluar_estado(1, AHORA)
        assert info.estado == EstadoCredencial.EN_GRACIA

    async def test_fail_open_a_vigente(self):
        servicio = ServicioExpiracionPassword(repo=_RepoQueFalla(), politica=_politica())
        info = await servicio.evaluar_estado(1, AHORA)
        assert info.estado == EstadoCredencial.VIGENTE


def _usuario(uid: int = 7) -> UsuarioEntity:
    return UsuarioEntity(
        uid=uid, nombre=str(uid), email="x@y.co", roles=[], activo=True,
        new_pass_hash="$2b$12$abcdefghijklmnopqrstuv",
    )


def _servicio_con_baseline(dias_atras: int) -> ServicioExpiracionPassword:
    # Siembra la linea base relativa al ahora real (el use case no recibe "ahora").
    repo = InMemoryPasswordExpiracionRepo()
    ahora_real = datetime.now(UTC).replace(tzinfo=None)
    repo._cambios[7] = ahora_real - timedelta(days=dias_atras)
    return ServicioExpiracionPassword(repo=repo, politica=_politica())


def _throttle() -> LoginThrottleService:
    return LoginThrottleService(
        store=InMemoryIntentosLoginStore(ttl_segundos=900), paso_segundos=5, maximo_segundos=30
    )


def _build_uc(expiracion, autenticar_return=_usuario()):
    auth = AsyncMock()
    auth.autenticar_async.return_value = autenticar_return
    auth.establecer_password_async = AsyncMock(return_value=None)
    auth.generar_token = MagicMock(return_value="tok")
    modulos = AsyncMock()
    modulos.obtener_modulos_por_uid_async.return_value = []
    estado = AsyncMock()
    estado.incrementar_version.return_value = 2

    async def fake_sleep(_s):
        return None

    return CambiarPasswordExpiradaUseCase(
        auth_service=auth,
        usuario_repo=AsyncMock(),
        modulos_repo=modulos,
        expiracion=expiracion,
        throttle=_throttle(),
        validador=None,
        sleeper=fake_sleep,
        estado_credencial=estado,
    ), auth, estado


class TestUseCase:
    async def test_en_gracia_cambia_y_emite_sesion(self):
        uc, auth, estado = _build_uc(_servicio_con_baseline(92))  # 2 dias vencida
        result = await uc.ejecutar_async("7", "vieja", "NuevaClave#2026", "k")
        assert result.token == "tok"
        auth.establecer_password_async.assert_awaited_once()
        estado.incrementar_version.assert_awaited_once()

    async def test_vigente_rechaza(self):
        uc, _a, _e = _build_uc(_servicio_con_baseline(10))  # vigente
        with pytest.raises(CredencialVigente):
            await uc.ejecutar_async("7", "vieja", "NuevaClave#2026", "k")

    async def test_fuera_de_gracia_rechaza(self):
        uc, _a, _e = _build_uc(_servicio_con_baseline(200))  # muy vencida
        with pytest.raises(CredencialVencidaFueraDeGracia):
            await uc.ejecutar_async("7", "vieja", "NuevaClave#2026", "k")

    async def test_password_incorrecta_rechaza(self):
        uc, _a, _e = _build_uc(_servicio_con_baseline(92), autenticar_return=None)
        with pytest.raises(CredencialesInvalidas):
            await uc.ejecutar_async("7", "mala", "NuevaClave#2026", "k")


def _build_login(expiracion, enforcement, autenticar_return=_usuario()):
    auth = AsyncMock()
    auth.autenticar_async.return_value = autenticar_return
    auth.generar_token = MagicMock(return_value="tok")
    modulos = AsyncMock()
    modulos.obtener_modulos_por_uid_async.return_value = []

    async def fake_sleep(_s):
        return None

    return LoginUseCase(
        auth_service=auth,
        throttle=_throttle(),
        usuario_repo=AsyncMock(),
        modulos_repo=modulos,
        sleeper=fake_sleep,
        expiracion=expiracion,
        enforcement_enabled=enforcement,
    )


class TestLoginEnforcement:
    async def test_login_en_gracia_lanza(self):
        uc = _build_login(_servicio_con_baseline(92), enforcement=True)
        with pytest.raises(CredencialEnGracia):
            await uc.ejecutar_async("7", "pw", "k")

    async def test_login_fuera_gracia_lanza(self):
        uc = _build_login(_servicio_con_baseline(200), enforcement=True)
        with pytest.raises(CredencialVencidaFueraDeGracia):
            await uc.ejecutar_async("7", "pw", "k")

    async def test_login_vigente_ok(self):
        uc = _build_login(_servicio_con_baseline(10), enforcement=True)
        result = await uc.ejecutar_async("7", "pw", "k")
        assert result.token == "tok"

    async def test_enforcement_deshabilitado_no_bloquea(self):
        uc = _build_login(_servicio_con_baseline(200), enforcement=False)
        result = await uc.ejecutar_async("7", "pw", "k")
        assert result.token == "tok"
