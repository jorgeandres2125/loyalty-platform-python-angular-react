from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ComisionistaProgramaEntity:
    """Programa de comisionistas — tabla comisionistas_programa."""
    cpid: int = 0
    cp_nombre: str = ""
