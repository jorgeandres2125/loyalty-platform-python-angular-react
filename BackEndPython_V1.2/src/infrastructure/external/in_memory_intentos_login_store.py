from __future__ import annotations

import asyncio
import time

from src.domain.value_objects.intentos_login import IntentosLogin


class InMemoryIntentosLoginStore:
    """Almacén en memoria de proceso del conteo de fallos de login (AP-0007).

    Implementa el puerto `IntentosLoginStore` (PEP 544): un dict protegido por
    `asyncio.Lock` y una marca de expiración del reloj monótono por entrada. El TTL
    es la ventana de reinicio: tras `ttl_segundos` sin nuevos fallos, el contador
    caduca y vuelve a empezar en cero.

    ⚠️ Ámbito de proceso: el estado NO se comparte entre workers de uvicorn ni
    réplicas, y se pierde al reiniciar. Suficiente para un único proceso de backend;
    al escalar horizontalmente, sustituir por un adaptador Redis/SQL — la firma del
    puerto no cambia.
    """

    def __init__(self, ttl_segundos: int) -> None:
        self._ttl_segundos: int = ttl_segundos
        self._datos: dict[str, tuple[IntentosLogin, float]] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def guardar(self, clave: str, registro: IntentosLogin) -> None:
        expira_en: float = time.monotonic() + self._ttl_segundos
        async with self._lock:
            self._datos[clave] = (registro, expira_en)

    async def obtener(self, clave: str) -> IntentosLogin | None:
        async with self._lock:
            par: tuple[IntentosLogin, float] | None = self._datos.get(clave)
            if par is None:
                return None
            registro: IntentosLogin
            expira_en: float
            registro, expira_en = par
            if time.monotonic() >= expira_en:
                del self._datos[clave]
                return None
            return registro

    async def eliminar(self, clave: str) -> None:
        async with self._lock:
            self._datos.pop(clave, None)
