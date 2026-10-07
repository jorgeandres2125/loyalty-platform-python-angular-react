from __future__ import annotations

import asyncio
import time


class InMemoryRevocacionTokenStore:
    """AP-0021: denylist de jti revocados en memoria de proceso con expiracion.

    Implementa RevocacionTokenStore (PEP 544). Cada jti revocado vive hasta su TTL (la
    vida restante del token) y luego se purga de forma perezosa. Ambito de proceso: no
    se comparte entre workers ni replicas y se pierde al reiniciar. En produccion,
    sustituir por Redis o el adaptador SQL (tabla revoked_token).
    """

    def __init__(self) -> None:
        self._revocados: dict[str, float] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def revocar(self, jti: str, ttl_segundos: int) -> None:
        async with self._lock:
            self._revocados[jti] = time.time() + max(0, ttl_segundos)

    async def esta_revocado(self, jti: str) -> bool:
        async with self._lock:
            expira: float | None = self._revocados.get(jti)
            if expira is None:
                return False
            if time.time() >= expira:
                del self._revocados[jti]
                return False
            return True
