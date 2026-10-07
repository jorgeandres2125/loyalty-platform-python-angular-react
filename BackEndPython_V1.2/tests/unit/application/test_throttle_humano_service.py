"""Tests para ThrottleHumanoService (gating de humano por retrasos — AP-0019)."""
from __future__ import annotations

import pytest

from src.application.services.throttle_humano_service import ThrottleHumanoService
from src.infrastructure.external.in_memory_intentos_login_store import InMemoryIntentosLoginStore


def _service(
    libres: int = 2, paso: int = 5, maximo: int = 30, ttl: int = 900
) -> ThrottleHumanoService:
    return ThrottleHumanoService(
        store=InMemoryIntentosLoginStore(ttl_segundos=ttl),
        intentos_libres=libres,
        paso_segundos=paso,
        maximo_segundos=maximo,
    )


@pytest.mark.asyncio
async def test_intentos_libres_no_aplican_retraso() -> None:
    svc = _service(libres=2)
    assert await svc.registrar_intento_async("registro|ip") == 0  # 1º libre
    assert await svc.registrar_intento_async("registro|ip") == 0  # 2º libre


@pytest.mark.asyncio
async def test_retraso_incremental_tras_los_libres() -> None:
    svc = _service(libres=2)
    esperas = [await svc.registrar_intento_async("registro|ip") for _ in range(6)]
    # 2 libres (0,0) y luego 5,10,15,20
    assert esperas == [0, 0, 5, 10, 15, 20]


@pytest.mark.asyncio
async def test_retraso_topa_en_maximo() -> None:
    svc = _service(libres=0, paso=5, maximo=30)
    esperas = [await svc.registrar_intento_async("k") for _ in range(8)]
    assert esperas == [5, 10, 15, 20, 25, 30, 30, 30]


@pytest.mark.asyncio
async def test_claves_independientes_por_accion_e_ip() -> None:
    svc = _service(libres=0)
    await svc.registrar_intento_async("registro|ipA")
    await svc.registrar_intento_async("registro|ipA")
    assert await svc.registrar_intento_async("registro|ipB") == 5  # otra IP parte de cero
    assert await svc.registrar_intento_async("reset|ipA") == 5      # otra acción, misma IP


@pytest.mark.asyncio
async def test_sin_libres_cobra_desde_el_primero() -> None:
    svc = _service(libres=0)
    assert await svc.registrar_intento_async("k") == 5
