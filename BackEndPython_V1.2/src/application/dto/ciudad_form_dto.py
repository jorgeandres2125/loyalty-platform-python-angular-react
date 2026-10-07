from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CiudadFormDTO:
    ciudad: str
    did: int | None = None
