from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ComisionistaSubprogramaEntity:
    """Subprograma de comisionistas — tabla comisionistas_subprograma."""
    cspid: int | None = None
    cspid_nombre: str = ""
    cpid: int | None = None
