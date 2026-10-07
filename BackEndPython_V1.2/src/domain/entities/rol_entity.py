from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RolEntity:
    """Rol del sistema — tabla dbo.role (rid, name).

    Es el sujeto de la parametrización de autorizaciones (AP-0054): cada rol
    recibe una matriz de permisos por módulo.
    """
    rid: int = 0
    name: str = ""
