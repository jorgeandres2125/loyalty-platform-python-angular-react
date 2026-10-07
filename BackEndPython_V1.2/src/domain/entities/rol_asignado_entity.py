from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RolAsignadoEntity:
    """Rol del sistema con la marca de si está asignado a un usuario dado (AP-0054).

    Alimenta la vista "roles por usuario": se listan todos los roles asignables y
    cada uno indica con `asignado` si el usuario lo tiene en dbo.users_roles.
    """

    rid: int = 0
    name: str = ""
    asignado: bool = False
