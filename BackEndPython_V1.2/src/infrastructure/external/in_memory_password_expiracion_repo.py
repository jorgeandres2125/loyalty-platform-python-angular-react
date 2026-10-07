from __future__ import annotations

from datetime import datetime


class InMemoryPasswordExpiracionRepo:
    """AP-0037: adaptador en memoria del reloj de vencimiento (para pruebas).

    Satisface PasswordExpiracionRepository (PEP 544). Guarda el instante del ultimo
    cambio por uid en un diccionario del proceso; util en pruebas y como fallback
    sin base de datos. El adaptador durable de produccion es el SQL.
    """

    def __init__(self) -> None:
        self._cambios: dict[int, datetime] = {}

    async def obtener_cambiado_en(self, uid: int) -> datetime | None:
        return self._cambios.get(uid)

    async def registrar_cambio(self, uid: int, cuando: datetime) -> None:
        self._cambios[uid] = cuando

    async def asegurar_baseline(self, uid: int, cuando: datetime) -> None:
        self._cambios.setdefault(uid, cuando)
