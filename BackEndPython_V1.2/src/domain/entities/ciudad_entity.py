from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CiudadEntity:
    """Ciudad — tabla dbo.ciudades."""
    cid: int = 0
    did: int | None = None
    ciudad: str = ""
