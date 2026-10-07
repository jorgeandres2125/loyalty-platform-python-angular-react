"""Tests para InMemoryIntentosLoginStore (conteo de fallos de login con TTL — AP-0007)."""
from __future__ import annotations

import pytest

from src.domain.value_objects.intentos_login import IntentosLogin
from src.infrastructure.external.in_memory_intentos_login_store import InMemoryIntentosLoginStore


def _registro(conteo: int = 1) -> IntentosLogin:
    return IntentosLogin(conteo=conteo, actualizado_en_monotonic=0.0)


@pytest.mark.asyncio
async def test_guardar_y_obtener() -> None:
    store = InMemoryIntentosLoginStore(ttl_segundos=60)
    await store.guardar("ip|user", _registro(3))
    recuperado = await store.obtener("ip|user")
    assert recuperado is not None
    assert recuperado.conteo == 3


@pytest.mark.asyncio
async def test_obtener_inexistente_devuelve_none() -> None:
    store = InMemoryIntentosLoginStore(ttl_segundos=60)
    assert await store.obtener("no-existe") is None


@pytest.mark.asyncio
async def test_eliminar() -> None:
    store = InMemoryIntentosLoginStore(ttl_segundos=60)
    await store.guardar("k", _registro())
    await store.eliminar("k")
    assert await store.obtener("k") is None


@pytest.mark.asyncio
async def test_expira_tras_ttl() -> None:
    # TTL = 0 → la entrada se considera expirada en la siguiente lectura.
    store = InMemoryIntentosLoginStore(ttl_segundos=0)
    await store.guardar("k", _registro())
    assert await store.obtener("k") is None
