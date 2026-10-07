from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.entities.usuario_cuenta_entity import UsuarioCuentaEntity


@dataclass
class PaginaUsuariosDTO:
    """Página de cuentas de usuario para las vistas de asignación de roles."""

    items: list[UsuarioCuentaEntity] = field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 10
