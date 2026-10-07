from __future__ import annotations

from dataclasses import dataclass

from src.domain.entities.modulo_permiso_entity import ModuloPermisoEntity
from src.domain.entities.usuario_entity import UsuarioEntity


@dataclass(frozen=True)
class LoginResult:
    """Resultado de un login exitoso: el token firmado, el usuario autenticado y sus
    módulos de frontend. Las cookies (HttpOnly + CSRF) son responsabilidad del
    adaptador HTTP, no del caso de uso.
    """

    token: str
    usuario: UsuarioEntity
    modulos: list[ModuloPermisoEntity]
