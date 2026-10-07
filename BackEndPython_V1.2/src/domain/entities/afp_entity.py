from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AfpEntity:
    """AFP / Fondo de pensiones — tabla dbo.afp (origen: taxonomia_afp de Drupal)."""
    tid: int = 0
    nombre: str = ""
    nit: str | None = None
