from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EpsFormDTO:
    nombre: str
    nit: str | None = None
