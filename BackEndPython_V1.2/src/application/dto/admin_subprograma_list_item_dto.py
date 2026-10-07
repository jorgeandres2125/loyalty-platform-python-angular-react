from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AdminSubprogramaListItemDTO:
    cspid: int
    cspid_nombre: str
    cpid: int | None
