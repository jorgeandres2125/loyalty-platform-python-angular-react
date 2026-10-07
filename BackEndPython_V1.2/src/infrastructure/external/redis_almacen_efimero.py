from __future__ import annotations

from typing import Any


class RedisAlmacenEfimero:
    """AP-0081: adaptador Redis del puerto AlmacenEfimeroDistribuido, para compartir los
    estados efimeros entre replicas en alta disponibilidad.

    El paquete `redis` se importa de forma perezosa dentro del constructor para no exigir la
    dependencia cuando la app corre en un unico proceso (desarrollo y pruebas) con el
    adaptador en memoria. El TTL se delega a Redis (SET con expiracion), de modo que la
    expiracion es consistente entre todas las replicas.
    """

    def __init__(self, redis_url: str) -> None:
        from redis.asyncio import Redis  # import perezoso: dependencia solo en produccion

        self._cliente: Any = Redis.from_url(redis_url, decode_responses=True)

    async def guardar(self, clave: str, valor: str, ttl_segundos: int) -> None:
        await self._cliente.set(clave, valor, ex=ttl_segundos)

    async def obtener(self, clave: str) -> str | None:
        valor: Any = await self._cliente.get(clave)
        return valor if valor is None else str(valor)

    async def eliminar(self, clave: str) -> None:
        await self._cliente.delete(clave)
