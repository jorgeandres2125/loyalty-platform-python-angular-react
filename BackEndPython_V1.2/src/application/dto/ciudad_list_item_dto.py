from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CiudadListItemDTO:
    cid: int
    did: int | None
    ciudad: str
