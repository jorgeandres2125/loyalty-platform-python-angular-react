from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ArlListItemDTO:
    tid: int
    nombre: str
    nit: str | None
