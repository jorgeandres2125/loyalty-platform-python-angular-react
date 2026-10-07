from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BancoFormDTO:
    nombre: str
    codigo: str | None = None
