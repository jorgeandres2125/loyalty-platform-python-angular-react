from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DepartamentoListItemDTO:
    did: int
    pid: int | None
    departamento: str
