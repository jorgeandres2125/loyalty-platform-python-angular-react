from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BancoEntity:
    """Banco — tabla dbo.bancos (origen: taxonomia_banco de Drupal)."""
    tid: int = 0
    nombre: str = ""
    codigo: str | None = None
