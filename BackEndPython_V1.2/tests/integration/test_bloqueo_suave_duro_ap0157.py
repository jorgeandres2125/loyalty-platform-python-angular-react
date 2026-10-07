"""AP-0157: bloqueo suave y bloqueo duro de cuentas, independientes y con precedencia.

El bloqueo suave (temporal/operativo) reutiliza AP-0009; el bloqueo duro
(administrativo/seguridad) es nuevo, no expira y solo lo retira personal autorizado. Ambos
son independientes, pueden coexistir y el duro tiene precedencia absoluta en el login.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.services.login_throttle_service import LoginThrottleService
from src.application.services.servicio_bloqueo_cuenta import ServicioBloqueoCuenta
from src.application.services.servicio_bloqueo_duro import ServicioBloqueoDuro
from src.application.use_cases.login_use_case import LoginUseCase
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.cuenta_bloqueada import CuentaBloqueada
from src.domain.exceptions.cuenta_bloqueo_duro import CuentaBloqueoDuro
from src.infrastructure.external.in_memory_bloqueo_cuenta_repo import (
    InMemoryBloqueoCuentaRepo,
)
from src.infrastructure.external.in_memory_bloqueo_duro_repo import (
    InMemoryBloqueoDuroRepo,
)
from src.infrastructure.external.in_memory_intentos_login_store import (
    InMemoryIntentosLoginStore,
)


class _Reloj:
    def __init__(self) -> None:
        self.ahora: float = 1000.0

    def __call__(self) -> float:
        return self.ahora


def _usuario(uid: int = 1) -> UsuarioEntity:
    return UsuarioEntity(uid=uid, nombre=str(uid), email="x@y.co", roles=[], activo=True)


def _svc_duro(reloj: _Reloj, enabled: bool = True) -> ServicioBloqueoDuro:
    return ServicioBloqueoDuro(repo=InMemoryBloqueoDuroRepo(), enabled=enabled, clock=reloj)


def _svc_suave(reloj: _Reloj) -> ServicioBloqueoCuenta:
    return ServicioBloqueoCuenta(
        repo=InMemoryBloqueoCuentaRepo(),
        enabled=True,
        max_intentos=3,
        duracion_minutos=30,
        auto_unlock=True,
        reset_on_success=True,
        count_non_existing=False,
        clock=reloj,
    )


class TestServicioBloqueoDuro:
    async def test_aplicar_bloquea_y_verificar_lanza(self) -> None:
        svc = _svc_duro(_Reloj())
        await svc.aplicar(uid=1, motivo="fraude", por_uid=99)
        with pytest.raises(CuentaBloqueoDuro) as exc:
            await svc.verificar_no_bloqueada(1)
        assert exc.value.motivo == "fraude"

    async def test_remover_libera(self) -> None:
        svc = _svc_duro(_Reloj())
        await svc.aplicar(uid=1, motivo="investigacion", por_uid=99)
        await svc.remover(uid=1, por_uid=99)
        await svc.verificar_no_bloqueada(1)

    async def test_no_expira_automaticamente(self) -> None:
        reloj = _Reloj()
        svc = _svc_duro(reloj)
        await svc.aplicar(uid=1, motivo="seguridad", por_uid=99)
        reloj.ahora += 10 * 365 * 24 * 3600  # diez anios
        with pytest.raises(CuentaBloqueoDuro):
            await svc.verificar_no_bloqueada(1)

    async def test_deshabilitado_no_bloquea(self) -> None:
        svc = _svc_duro(_Reloj(), enabled=False)
        await svc.aplicar(uid=1, motivo="x", por_uid=99)
        await svc.verificar_no_bloqueada(1)

    async def test_consultar_devuelve_estado(self) -> None:
        svc = _svc_duro(_Reloj())
        assert await svc.consultar(1) is None
        await svc.aplicar(uid=1, motivo="m", por_uid=99)
        estado = await svc.consultar(1)
        assert estado is not None and estado.activo and estado.motivo == "m"


def _login_uc(
    reloj: _Reloj,
    suave: ServicioBloqueoCuenta | None,
    duro: ServicioBloqueoDuro | None,
) -> LoginUseCase:
    auth = AsyncMock()
    auth.autenticar_async.return_value = _usuario()
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
        bloqueo=suave,
        bloqueo_duro=duro,
    )


class TestPrecedenciaEnLogin:
    async def test_solo_duro_deniega_por_bloqueo_duro(self) -> None:
        reloj = _Reloj()
        duro = _svc_duro(reloj)
        await duro.aplicar(uid=1, motivo="fraude", por_uid=99)
        uc = _login_uc(reloj, suave=None, duro=duro)
        with pytest.raises(CuentaBloqueoDuro):
            await uc.ejecutar_async("1", "ok", "ip|1")

    async def test_solo_suave_deniega_por_bloqueo_suave(self) -> None:
        reloj = _Reloj()
        suave = _svc_suave(reloj)
        await suave.bloquear_manual("1", duracion_minutos=30, motivo="operativo")
        uc = _login_uc(reloj, suave=suave, duro=_svc_duro(reloj))
        with pytest.raises(CuentaBloqueada):
            await uc.ejecutar_async("1", "ok", "ip|1")

    async def test_ambos_gana_el_duro(self) -> None:
        # Coexistencia: ambos activos; el duro tiene precedencia absoluta.
        reloj = _Reloj()
        suave = _svc_suave(reloj)
        duro = _svc_duro(reloj)
        await suave.bloquear_manual("1", duracion_minutos=30, motivo="operativo")
        await duro.aplicar(uid=1, motivo="seguridad", por_uid=99)
        uc = _login_uc(reloj, suave=suave, duro=duro)
        with pytest.raises(CuentaBloqueoDuro):
            await uc.ejecutar_async("1", "ok", "ip|1")

    async def test_sin_bloqueos_autentica(self) -> None:
        reloj = _Reloj()
        uc = _login_uc(reloj, suave=_svc_suave(reloj), duro=_svc_duro(reloj))
        resultado = await uc.ejecutar_async("1", "ok", "ip|1")
        assert resultado.token == "tok"


class TestIndependenciaDeBloqueos:
    async def test_remover_suave_no_afecta_al_duro(self) -> None:
        reloj = _Reloj()
        suave = _svc_suave(reloj)
        duro = _svc_duro(reloj)
        await suave.bloquear_manual("1", duracion_minutos=30, motivo="op")
        await duro.aplicar(uid=1, motivo="seg", por_uid=99)
        await suave.desbloquear("1")
        await suave.verificar_no_bloqueada("1")  # suave liberado
        with pytest.raises(CuentaBloqueoDuro):
            await duro.verificar_no_bloqueada(1)  # duro intacto

    async def test_aplicar_suave_no_afecta_al_duro(self) -> None:
        reloj = _Reloj()
        suave = _svc_suave(reloj)
        duro = _svc_duro(reloj)
        await duro.aplicar(uid=1, motivo="seg", por_uid=99)
        await suave.bloquear_manual("1", duracion_minutos=30, motivo="op")
        estado = await duro.consultar(1)
        assert estado is not None and estado.activo and estado.motivo == "seg"

    async def test_remover_duro_no_afecta_al_suave(self) -> None:
        reloj = _Reloj()
        suave = _svc_suave(reloj)
        duro = _svc_duro(reloj)
        await suave.bloquear_manual("1", duracion_minutos=30, motivo="op")
        await duro.aplicar(uid=1, motivo="seg", por_uid=99)
        await duro.remover(uid=1, por_uid=99)
        estado = await suave.consultar("1")
        assert estado is not None and estado.bloqueada and estado.motivo == "op"


class TestBloqueoSuaveAdministrativo:
    async def test_bloquear_manual_expira_tras_la_duracion(self) -> None:
        reloj = _Reloj()
        suave = _svc_suave(reloj)
        await suave.bloquear_manual("1", duracion_minutos=30, motivo="op")
        with pytest.raises(CuentaBloqueada):
            await suave.verificar_no_bloqueada("1")
        reloj.ahora += 30 * 60 + 1
        await suave.verificar_no_bloqueada("1")  # auto-unlock

    async def test_consultar_expone_motivo(self) -> None:
        reloj = _Reloj()
        suave = _svc_suave(reloj)
        await suave.bloquear_manual("1", duracion_minutos=30, motivo="suspension operativa")
        estado = await suave.consultar("1")
        assert estado is not None and estado.motivo == "suspension operativa"
