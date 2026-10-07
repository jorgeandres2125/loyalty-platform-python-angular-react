from __future__ import annotations

import pytest

from src.application.services.servicio_bloqueo_cuenta import ServicioBloqueoCuenta
from src.application.services.servicio_sesiones import ServicioSesiones
from src.application.services.validador_sesion import ValidadorSesion
from src.domain.exceptions.sesion_invalida import SesionInvalida
from src.domain.services.politica_sesiones import PoliticaSesiones
from src.infrastructure.external.in_memory_bloqueo_cuenta_repo import InMemoryBloqueoCuentaRepo
from src.infrastructure.external.in_memory_estado_credencial_repo import (
    InMemoryEstadoCredencialRepo,
)
from src.infrastructure.external.in_memory_revocacion_token_store import (
    InMemoryRevocacionTokenStore,
)
from src.infrastructure.external.in_memory_sesion_repo import InMemorySesionRepo


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


def _servicio_sesiones() -> ServicioSesiones:
    politica = PoliticaSesiones(max_canal=0, max_otras=0, roles_canal=frozenset())
    return ServicioSesiones(repo=InMemorySesionRepo(), politica=politica, habilitado=True)


def _validador(sesiones: ServicioSesiones | None) -> ValidadorSesion:
    return ValidadorSesion(
        estado_repo=InMemoryEstadoCredencialRepo(),
        denylist=InMemoryRevocacionTokenStore(),
        bloqueo=_bloqueo(),
        sesiones=sesiones,
    )


async def test_sin_servicio_sesiones_no_verifica_sid() -> None:
    # Retrocompatibilidad: sesiones=None (config deshabilitada) no cambia el comportamiento previo.
    v = _validador(None)
    await v.validar({"sub": "1", "nombre": "juan", "tv": 1, "jti": "j1", "sid": "s1"})


async def test_sid_no_registrado_pasa() -> None:
    # Un token emitido antes de habilitar AP-0130, o sin sid, no debe bloquearse.
    v = _validador(_servicio_sesiones())
    await v.validar({"sub": "1", "nombre": "juan", "tv": 1, "jti": "j1", "sid": "desconocido"})


async def test_sid_revocado_falla() -> None:
    sesiones = _servicio_sesiones()
    await sesiones.registrar(
        sid="s1", uid=1, roles=[], jti="j1", device_fp="fp", ip="127.0.0.1", user_agent="pytest"
    )
    await sesiones.revocar(uid=1, sid="s1")
    v = _validador(sesiones)
    with pytest.raises(SesionInvalida):
        await v.validar({"sub": "1", "nombre": "juan", "tv": 1, "jti": "j1", "sid": "s1"})


async def test_sid_activo_pasa() -> None:
    sesiones = _servicio_sesiones()
    await sesiones.registrar(
        sid="s1", uid=1, roles=[], jti="j1", device_fp="fp", ip="127.0.0.1", user_agent="pytest"
    )
    v = _validador(sesiones)
    await v.validar({"sub": "1", "nombre": "juan", "tv": 1, "jti": "j1", "sid": "s1"})


async def test_sin_claim_sid_no_consulta_registro() -> None:
    v = _validador(_servicio_sesiones())
    await v.validar({"sub": "1", "nombre": "juan", "tv": 1, "jti": "j1"})
