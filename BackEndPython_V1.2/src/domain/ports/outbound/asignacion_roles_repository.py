from __future__ import annotations

from typing import Protocol

from src.domain.entities.rol_asignado_entity import RolAsignadoEntity
from src.domain.entities.rol_entity import RolEntity
from src.domain.entities.usuario_cuenta_entity import UsuarioCuentaEntity


class AsignacionRolesRepository(Protocol):
    """Puerto de salida para la asignación de roles a usuarios (AP-0054).

    Opera sobre dbo.role, dbo.users y dbo.users_roles. Devuelve y recibe
    entidades de dominio; el adaptador SQLAlchemy traduce a/desde los modelos.
    """

    async def listar_roles_asignables_async(self) -> list[RolEntity]: ...

    async def existe_rol_async(self, rid: int) -> bool: ...

    async def obtener_nombre_rol_async(self, rid: int) -> str | None: ...

    async def obtener_usuario_async(self, uid: int) -> UsuarioCuentaEntity | None: ...

    async def listar_usuarios_de_rol_async(
        self, rid: int, texto: str | None, page: int, page_size: int
    ) -> tuple[list[UsuarioCuentaEntity], int]: ...

    async def buscar_usuarios_async(
        self, texto: str | None, page: int, page_size: int
    ) -> tuple[list[UsuarioCuentaEntity], int]: ...

    async def obtener_roles_de_usuario_async(self, uid: int) -> list[RolAsignadoEntity]: ...

    async def asignar_rol_async(self, uid: int, rid: int) -> bool: ...

    async def quitar_rol_async(self, uid: int, rid: int) -> bool: ...
