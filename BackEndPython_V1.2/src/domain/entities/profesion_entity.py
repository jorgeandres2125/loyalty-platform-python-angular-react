from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProfesionEntity:
    """Término de profesión — tabla taxonomia_profesion."""
    tid: int = 0
    nombre: str = ""
