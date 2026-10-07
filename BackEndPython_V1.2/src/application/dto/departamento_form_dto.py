from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DepartamentoFormDTO:
    departamento: str
    pid: int | None = None
