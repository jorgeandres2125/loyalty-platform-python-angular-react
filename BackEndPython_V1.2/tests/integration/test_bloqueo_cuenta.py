from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.services.login_throttle_service import LoginThrottleService
from src.application.services.servicio_bloqueo_cuenta import ServicioBloqueoCuenta
from src.application.use_cases.login_use_case import LoginUseCase
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.credenciales_invalidas import CredencialesInvalidas
from src.domain.exceptions.cuenta_bloqueada import CuentaBloqueada
from src.infrastructure.external.in_memory_bloqueo_cuenta_repo import InMemoryBloqueoCuentaRepo
from src.infrastructure.external.in_memory_intentos_login_store import InMemoryIntentosLoginStore


class _Reloj:
    def __init__(self) -> None:
        self.ahora = 1000.0

    def __call__(self) -> float:
        return self.ahora


def _servicio(
    reloj: _Reloj,
    enabled: bool = True,
    max_intentos: int = 3,
    duracion_minutos: int = 15,
    auto_unlock: bool = True,
    reset_on_success: bool = True,
    count_non_existing: bool = False,
) -> ServicioBloqueoCuenta:
    return ServicioBloqueoCuenta(
        repo=InMemoryBloqueoCuentaRepo(),
        enabled=enabled,
        max_intentos=max_intentos,
        duracion_minutos=duracion_minutos,
        auto_unlock=auto_unlock,
        reset_on_success=reset_on_success,
        count_non_existing=count_non_existing,
        clock=reloj,
    )


class TestServicioBloqueo:
    async def test_bloquea_al_alcanzar_maximo(self) -> None:
        reloj = _Reloj()
        svc = _servicio(reloj, max_intentos=3)
        await svc.registrar_fallo("juan", existe=True)
        await svc.registrar_fallo("juan", existe=True)
        await svc.verificar_no_bloqueada("juan")
        await svc.registrar_fallo("juan", existe=True)
        with pytest.raises(CuentaBloqueada):
            await svc.verificar_no_bloqueada("juan")

    async def test_desbloqueo_automatico_tras_expirar(self) -> None:
        reloj = _Reloj()
        svc = _servicio(reloj, max_intentos=1, duracion_minutos=15)
        await svc.registrar_fallo("ana", existe=True)
        with pytest.raises(CuentaBloqueada):
            await svc.verificar_no_bloqueada("ana")
        reloj.ahora += 15 * 60 + 1
        await svc.verificar_no_bloqueada("ana")

    async def test_exito_reinicia_contador(self) -> None:
        reloj = _Reloj()
        svc = _servicio(reloj, max_intentos=2)
        await svc.registrar_fallo("p", existe=True)
        await svc.registrar_exito("p")
        await svc.registrar_fallo("p", existe=True)
        await svc.verificar_no_bloqueada("p")

    async def test_no_cuenta_inexistentes_por_defecto(self) -> None:
        reloj = _Reloj()
        svc = _servicio(reloj, max_intentos=1, count_non_existing=False)
        await svc.registrar_fallo("fantasma", existe=False)
        await svc.verificar_no_bloqueada("fantasma")

    async def test_cuenta_inexistentes_si_configurado(self) -> None:
        reloj = _Reloj()
        svc = _servicio(reloj, max_intentos=1, count_non_existing=True)
        await svc.registrar_fallo("fantasma", existe=False)
        with pytest.raises(CuentaBloqueada):
            await svc.verificar_no_bloqueada("fantasma")

    async def test_deshabilitado_no_bloquea(self) -> None:
        reloj = _Reloj()
        svc = _servicio(reloj, enabled=False, max_intentos=1)
        await svc.registrar_fallo("x", existe=True)
        await svc.verificar_no_bloqueada("x")

    async def test_bloqueo_permanente_sin_auto_unlock(self) -> None:
        reloj = _Reloj()
        svc = _servicio(reloj, max_intentos=1, auto_unlock=False)
        await svc.registrar_fallo("x", existe=True)
        with pytest.raises(CuentaBloqueada) as exc:
            await svc.verificar_no_bloqueada("x")
        assert exc.value.segundos_restantes is None
        reloj.ahora += 100000
        with pytest.raises(CuentaBloqueada):
            await svc.verificar_no_bloqueada("x")

    async def test_desbloqueo_manual(self) -> None:
        reloj = _Reloj()
        svc = _servicio(reloj, max_intentos=1)
        await svc.registrar_fallo("x", existe=True)
        await svc.desbloquear("x")
        await svc.verificar_no_bloqueada("x")


def _usuario(uid: int = 1) -> UsuarioEntity:
    return UsuarioEntity(uid=uid, nombre=str(uid), email="x@y.co", roles=[], activo=True)


async def _no_sleep(_s: float) -> None:
    return None


def _login_uc(bloqueo: ServicioBloqueoCuenta, side_effect) -> LoginUseCase:
    auth = AsyncMock()
    auth.autenticar_async.side_effect = side_effect
    auth.generar_token = MagicMock(return_value="tok")
    throttle = LoginThrottleService(
        store=InMemoryIntentosLoginStore(ttl_segundos=900),
        paso_segundos=5,
        maximo_segundos=30,
    )
    modulos_repo = AsyncMock()
    modulos_repo.obtener_modulos_por_uid_async.return_value = []
    usuario_repo = AsyncMock()
    usuario_repo.obtener_por_nombre_async.return_value = _usuario()
    return LoginUseCase(
        auth_service=auth,
        throttle=throttle,
        usuario_repo=usuario_repo,
        modulos_repo=modulos_repo,
        sleeper=_no_sleep,
        bloqueo=bloqueo,
    )


class TestLoginConBloqueo:
    async def test_se_bloquea_tras_maximos_fallos(self) -> None:
        reloj = _Reloj()
        svc = _servicio(reloj, max_intentos=3)
        uc = _login_uc(svc, side_effect=[None, None, None])
        for _ in range(3):
            with pytest.raises(CredencialesInvalidas):
                await uc.ejecutar_async("Juan", "bad", "ip|juan")
        with pytest.raises(CuentaBloqueada):
            await uc.ejecutar_async("Juan", "bad", "ip|juan")

    async def test_exito_reinicia_y_no_bloquea(self) -> None:
        reloj = _Reloj()
        svc = _servicio(reloj, max_intentos=3)
        uc = _login_uc(svc, side_effect=[None, None, _usuario(), None, None])
        with pytest.raises(CredencialesInvalidas):
            await uc.ejecutar_async("Ana", "b", "k")
        with pytest.raises(CredencialesInvalidas):
            await uc.ejecutar_async("Ana", "b", "k")
        await uc.ejecutar_async("Ana", "ok", "k")
        with pytest.raises(CredencialesInvalidas):
            await uc.ejecutar_async("Ana", "b", "k")
        with pytest.raises(CredencialesInvalidas):
            await uc.ejecutar_async("Ana", "b", "k")
        await svc.verificar_no_bloqueada("ana")
