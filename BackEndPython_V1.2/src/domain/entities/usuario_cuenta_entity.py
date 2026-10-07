from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UsuarioCuentaEntity:
    """Cuenta de usuario en el contexto de asignación de roles (AP-0054).

    Vista ligera de dbo.users: solo los campos necesarios para listar/buscar
    cuentas y asignarles roles. No transporta hashes de contraseña.
    """

    uid: int = 0
    nombre: str = ""
    email: str = ""
    activo: bool = True
