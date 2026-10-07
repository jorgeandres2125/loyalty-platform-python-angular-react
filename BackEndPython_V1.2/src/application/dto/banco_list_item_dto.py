from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BancoListItemDTO:
    tid: int
    nombre: str
    codigo: str | None
