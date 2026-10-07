from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AdminSubprogramaFormDTO:
    cspid_nombre: str
    cpid: int | None = None
