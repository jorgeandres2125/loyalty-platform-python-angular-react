from __future__ import annotations

import asyncio
import time


class InMemoryAlmacenEfimero:
    """AP-0081: adaptador en memoria de proceso del puerto AlmacenEfimeroDistribuido.

    Clave-valor con expiracion TTL basada en el reloj monotono, protegido por un
    asyncio.Lock. Ambito de un unico proceso: NO comparte estado entre replicas. Es el
    adaptador por defecto en desarrollo y pruebas; en produccion multi-replica se sustituye
    por el adaptador Redis sin cambiar la firma del puerto.
    """

    def __init__(self) -> None:
        self._datos: dict[str, tuple[str, float]] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def guardar(self, clave: str, valor: str, ttl_segundos: int) -> None:
        expira_en: float = time.monotonic() + ttl_segundos
        async with self._lock:
            self._datos[clave] = (valor, expira_en)

    async def obtener(self, clave: str) -> str | None:
        async with self._lock:
            par: tuple[str, float] | None = self._datos.get(clave)
            if par is None:
                return None
            valor: str
            expira_en: float
            valor, expira_en = par
            if time.monotonic() >= expira_en:
                del self._datos[clave]
                return None
            return valor

    async def eliminar(self, clave: str) -> None:
        async with self._lock:
            self._datos.pop(clave, None)
