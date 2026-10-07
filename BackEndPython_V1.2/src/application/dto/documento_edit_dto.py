from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class DocumentoEditDTO:
    did: int
    nombre: str | None = None
    estado: str | None = None
    fecha: datetime | None = None
