from __future__ import annotations

from typing import Protocol

from src.domain.entities.modulo_permiso_entity import ModuloPermisoEntity


class FrontendModulesRepository(Protocol):
    async def obtener_modulos_por_uid_async(self, uid: int) -> list[ModuloPermisoEntity]: ...
