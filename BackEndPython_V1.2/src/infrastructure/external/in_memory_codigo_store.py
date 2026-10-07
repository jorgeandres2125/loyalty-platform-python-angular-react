from __future__ import annotations

import asyncio
import time

from src.domain.value_objects.codigo_verificacion import CodigoVerificacion


class InMemoryCodigoStore:
    """Almacén OTP en memoria de proceso con expiración TTL (AP-0004).

    Implementa el puerto `CodigoVerificacionStore` (PEP 544) sin dependencias
    externas: un dict protegido por `asyncio.Lock` y una marca de expiración del
    reloj monótono por entrada.

    ⚠️ Ámbito de proceso: el estado NO se comparte entre workers de uvicorn ni
    réplicas, y se pierde al reiniciar. Suficiente para un único proceso de
    backend; al escalar horizontalmente, sustituir por un adaptador Redis/SQL —
    la firma del puerto no cambia.
    """

    def __init__(self, ttl_segundos: int) -> None:
        self._ttl_segundos: int = ttl_segundos
        self._datos: dict[str, tuple[CodigoVerificacion, float]] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def guardar(self, clave: str, registro: CodigoVerificacion) -> None:
        expira_en: float = time.monotonic() + self._ttl_segundos
        async with self._lock:
            self._datos[clave] = (registro, expira_en)

    async def obtener(self, clave: str) -> CodigoVerificacion | None:
        async with self._lock:
            par: tuple[CodigoVerificacion, float] | None = self._datos.get(clave)
            if par is None:
                return None
            registro: CodigoVerificacion
            expira_en: float
            registro, expira_en = par
            if time.monotonic() >= expira_en:
                del self._datos[clave]
                return None
            return registro

    async def eliminar(self, clave: str) -> None:
        async with self._lock:
            self._datos.pop(clave, None)
