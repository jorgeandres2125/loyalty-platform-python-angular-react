from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class EstadoSincronizacionDTO:
    """AP-0144: resultado de comparar la hora del sistema con la hora oficial."""

    hora_sistema: datetime
    hora_oficial: datetime
    desfase_segundos: float
    sincronizado: bool
    umbral_segundos: int
