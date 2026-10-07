from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class ReporteRequestDTO:
    tipo: int
    programa: int = 1
    subprograma: int | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    cedula: str | None = None
    estado: int | None = None
    page: int = 1
    page_size: int = 10
