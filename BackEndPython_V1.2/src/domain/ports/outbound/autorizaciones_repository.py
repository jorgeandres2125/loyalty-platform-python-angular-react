from __future__ import annotations

from typing import Protocol

from src.domain.entities.autorizacion_modulo_entity import AutorizacionModuloEntity
from src.domain.entities.rol_entity import RolEntity
from src.domain.value_objects.permisos_modulo import PermisosModulo


class AutorizacionesRepository(Protocol):
    """Puerto outbound para parametrizar autorizaciones (AP-0054).

    Modelo: matriz rol (dbo.role) × módulo (dbo.frontend_modules) → 6 flags de
    permiso (dbo.frontend_modules_permissions). El repositorio expone los roles,
    la matriz de un rol (todos los módulos activos con sus flags) y el upsert de
    los flags de un par (rol, módulo).
    """

    async def listar_roles_async(self) -> list[RolEntity]: ...

    async def obtener_matriz_por_rol_async(
        self, rid: int
    ) -> list[AutorizacionModuloEntity]: ...

    async def actualizar_permisos_async(
        self, rid: int, module_id: int, flags: PermisosModulo
    ) -> AutorizacionModuloEntity | None: ...

    async def actualizar_activo_modulo_async(
        self, module_id: int, activo: bool
    ) -> object: ...
