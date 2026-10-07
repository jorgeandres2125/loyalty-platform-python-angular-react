"""Tests para LoginThrottleService (retraso incremental ante fallos — AP-0007)."""
from __future__ import annotations

import pytest

from src.application.services.login_throttle_service import LoginThrottleService
from src.infrastructure.external.in_memory_intentos_login_store import InMemoryIntentosLoginStore


def _service(paso: int = 5, maximo: int = 30, ttl: int = 900) -> LoginThrottleService:
    return LoginThrottleService(
        store=InMemoryIntentosLoginStore(ttl_segundos=ttl),
        paso_segundos=paso,
        maximo_segundos=maximo,
    )


@pytest.mark.asyncio
async def test_retraso_incrementa_de_5_en_5() -> None:
    svc = _service()
    esperas = [await svc.registrar_fallo_async("ip|u") for _ in range(5)]
    assert esperas == [5, 10, 15, 20, 25]


@pytest.mark.asyncio
async def test_retraso_tope_en_30() -> None:
    svc = _service()
    for _ in range(5):
        await svc.registrar_fallo_async("ip|u")
    assert await svc.registrar_fallo_async("ip|u") == 30  # 6º fallo
    assert await svc.registrar_fallo_async("ip|u") == 30  # 7º sigue topado


@pytest.mark.asyncio
async def test_exito_reinicia_el_contador() -> None:
    svc = _service()
    await svc.registrar_fallo_async("ip|u")  # 5
    await svc.registrar_fallo_async("ip|u")  # 10
    await svc.reiniciar_async("ip|u")
    assert await svc.registrar_fallo_async("ip|u") == 5  # vuelve a empezar


@pytest.mark.asyncio
async def test_claves_distintas_son_independientes() -> None:
    svc = _service()
    await svc.registrar_fallo_async("ipA|u")
    await svc.registrar_fallo_async("ipA|u")
    assert await svc.registrar_fallo_async("ipB|u") == 5  # otra clave parte de cero


@pytest.mark.asyncio
async def test_paso_y_maximo_configurables() -> None:
    svc = _service(paso=3, maximo=9)
    esperas = [await svc.registrar_fallo_async("k") for _ in range(4)]
    assert esperas == [3, 6, 9, 9]
