from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class EstadoSincronizacionResponse(BaseModel):
    verificacion_habilitada: bool
    hora_sistema: datetime
    hora_oficial: datetime | None = None
    desfase_segundos: float | None = None
    sincronizado: bool | None = None
    umbral_segundos: int | None = None
    detalle: str | None = None
