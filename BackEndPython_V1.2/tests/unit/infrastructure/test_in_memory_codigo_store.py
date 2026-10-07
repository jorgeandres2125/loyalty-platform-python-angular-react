"""Tests para InMemoryCodigoStore (almacén OTP con TTL — AP-0004)."""
from __future__ import annotations

import pytest

from src.domain.value_objects.codigo_verificacion import CodigoVerificacion
from src.infrastructure.external.in_memory_codigo_store import InMemoryCodigoStore


def _registro() -> CodigoVerificacion:
    return CodigoVerificacion(codigo_hash="abc", intentos_restantes=5, creado_en_monotonic=0.0)


@pytest.mark.asyncio
async def test_guardar_y_obtener() -> None:
    store = InMemoryCodigoStore(ttl_segundos=60)
    await store.guardar("C.C.:123", _registro())
    recuperado = await store.obtener("C.C.:123")
    assert recuperado is not None
    assert recuperado.codigo_hash == "abc"


@pytest.mark.asyncio
async def test_obtener_inexistente_devuelve_none() -> None:
    store = InMemoryCodigoStore(ttl_segundos=60)
    assert await store.obtener("no-existe") is None


@pytest.mark.asyncio
async def test_eliminar() -> None:
    store = InMemoryCodigoStore(ttl_segundos=60)
    await store.guardar("k", _registro())
    await store.eliminar("k")
    assert await store.obtener("k") is None


@pytest.mark.asyncio
async def test_expira_tras_ttl() -> None:
    # TTL = 0 → la entrada se considera expirada en la siguiente lectura.
    store = InMemoryCodigoStore(ttl_segundos=0)
    await store.guardar("k", _registro())
    assert await store.obtener("k") is None
