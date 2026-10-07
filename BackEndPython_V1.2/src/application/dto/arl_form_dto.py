from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ArlFormDTO:
    nombre: str
    nit: str | None = None
