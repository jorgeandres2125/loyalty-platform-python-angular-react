from __future__ import annotations

import asyncio

from src.domain.entities.bloqueo_cuenta import BloqueoCuenta


class InMemoryBloqueoCuentaRepo:
    """AP-0009: estado de bloqueo de cuentas en memoria de proceso.

    Implementa BloqueoCuentaRepository (PEP 544): un dict protegido por asyncio.Lock,
    indexado por la clave de cuenta (nombre de usuario normalizado). Ambito de proceso:
    no se comparte entre workers ni replicas y se pierde al reiniciar. En produccion,
    sustituir por el adaptador SQL (tabla user_lockout) sin cambiar la firma del puerto.
    """

    def __init__(self) -> None:
        self._datos: dict[str, BloqueoCuenta] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def obtener(self, clave: str) -> BloqueoCuenta | None:
        async with self._lock:
            return self._datos.get(clave)

    async def guardar(self, estado: BloqueoCuenta) -> None:
        async with self._lock:
            self._datos[estado.clave] = estado

    async def eliminar(self, clave: str) -> None:
        async with self._lock:
            self._datos.pop(clave, None)
