from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AfpListItemDTO:
    tid: int
    nombre: str
    nit: str | None
