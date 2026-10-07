from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DepartamentoEntity:
    """Departamento — tabla dbo.departamentos."""
    did: int = 0
    pid: int | None = None
    departamento: str = ""
