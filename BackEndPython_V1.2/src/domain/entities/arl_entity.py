from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ArlEntity:
    """ARL — tabla dbo.arl (origen: taxonomia_arp de Drupal)."""
    tid: int = 0
    nombre: str = ""
    nit: str | None = None
