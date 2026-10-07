from __future__ import annotations

import asyncio
import time

from src.domain.entities.desafio_oob import DesafioOob


class InMemoryDesafioOobStore:
    """AP-0005: almacen de desafios OOB en memoria de proceso con TTL absoluto.

    Implementa el puerto DesafioOobStore (PEP 544): un dict protegido por asyncio.Lock
    con una marca de expiracion (reloj monotono) por desafio. El TTL es ABSOLUTO desde
    la creacion: actualizar el desafio (consumir un intento, rechazar) conserva la
    expiracion original y no reinicia el reloj.

    Ambito de proceso: el estado NO se comparte entre workers ni replicas y se pierde
    al reiniciar. Al escalar horizontalmente, sustituir por un adaptador Redis o SQL
    sin cambiar la firma del puerto.
    """

    def __init__(self, ttl_segundos: int) -> None:
        self._ttl_segundos: int = ttl_segundos
        self._datos: dict[str, tuple[DesafioOob, float]] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def guardar(self, desafio_id: str, desafio: DesafioOob) -> None:
        async with self._lock:
            existente: tuple[DesafioOob, float] | None = self._datos.get(desafio_id)
            expira_en: float = (
                existente[1]
                if existente is not None
                else time.monotonic() + self._ttl_segundos
            )
            self._datos[desafio_id] = (desafio, expira_en)

    async def obtener(self, desafio_id: str) -> DesafioOob | None:
        async with self._lock:
            par: tuple[DesafioOob, float] | None = self._datos.get(desafio_id)
            if par is None:
                return None
            desafio: DesafioOob
            expira_en: float
            desafio, expira_en = par
            if time.monotonic() >= expira_en:
                del self._datos[desafio_id]
                return None
            return desafio

    async def eliminar(self, desafio_id: str) -> None:
        async with self._lock:
            self._datos.pop(desafio_id, None)
