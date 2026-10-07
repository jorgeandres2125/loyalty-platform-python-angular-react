from __future__ import annotations

import asyncio

from src.infrastructure.external.in_memory_almacen_efimero import InMemoryAlmacenEfimero


def test_guardar_y_obtener() -> None:
    almacen = InMemoryAlmacenEfimero()
    asyncio.run(almacen.guardar("clave", "valor", ttl_segundos=60))
    assert asyncio.run(almacen.obtener("clave")) == "valor"


def test_obtener_inexistente_devuelve_none() -> None:
    almacen = InMemoryAlmacenEfimero()
    assert asyncio.run(almacen.obtener("no-existe")) is None


def test_expira_por_ttl() -> None:
    almacen = InMemoryAlmacenEfimero()

    async def _flujo() -> str | None:
        await almacen.guardar("clave", "valor", ttl_segundos=0)
        await asyncio.sleep(0.01)
        return await almacen.obtener("clave")

    assert asyncio.run(_flujo()) is None


def test_eliminar() -> None:
    almacen = InMemoryAlmacenEfimero()

    async def _flujo() -> str | None:
        await almacen.guardar("clave", "valor", ttl_segundos=60)
        await almacen.eliminar("clave")
        return await almacen.obtener("clave")

    assert asyncio.run(_flujo()) is None
