from __future__ import annotations

import asyncio
import time

from src.domain.entities.desafio_otp_login import DesafioOtpLogin


class InMemoryDesafioOtpStore:
    """AP-0012: almacen de desafios OTP de login en memoria de proceso con TTL absoluto.

    Implementa DesafioOtpStore (PEP 544). El TTL es absoluto desde la creacion: consumir
    un intento no reinicia el reloj. Ambito de proceso: no se comparte entre workers ni
    replicas y se pierde al reiniciar; en produccion, sustituir por Redis o SQL sin
    cambiar la firma del puerto.
    """

    def __init__(self, ttl_segundos: int) -> None:
        self._ttl_segundos: int = ttl_segundos
        self._datos: dict[str, tuple[DesafioOtpLogin, float]] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def guardar(self, desafio_id: str, desafio: DesafioOtpLogin) -> None:
        async with self._lock:
            existente: tuple[DesafioOtpLogin, float] | None = self._datos.get(desafio_id)
            expira_en: float = (
                existente[1]
                if existente is not None
                else time.monotonic() + self._ttl_segundos
            )
            self._datos[desafio_id] = (desafio, expira_en)

    async def obtener(self, desafio_id: str) -> DesafioOtpLogin | None:
        async with self._lock:
            par: tuple[DesafioOtpLogin, float] | None = self._datos.get(desafio_id)
            if par is None:
                return None
            desafio: DesafioOtpLogin
            expira_en: float
            desafio, expira_en = par
            if time.monotonic() >= expira_en:
                del self._datos[desafio_id]
                return None
            return desafio

    async def eliminar(self, desafio_id: str) -> None:
        async with self._lock:
            self._datos.pop(desafio_id, None)
