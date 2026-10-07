from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EpsEntity:
    """EPS — tabla dbo.eps (origen: taxonomia_eps de Drupal)."""
    tid: int = 0
    nombre: str = ""
    nit: str | None = None
