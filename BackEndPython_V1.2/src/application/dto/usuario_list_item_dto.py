from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UsuarioListItemDTO:
    uid: int
    nombre: str
    email: str
    activo: bool
    roles: list[str] = field(default_factory=list)
