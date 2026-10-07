from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.autorizacion_modulo_entity import AutorizacionModuloEntity
from src.domain.entities.rol_entity import RolEntity
from src.domain.value_objects.permisos_modulo import PermisosModulo
from src.infrastructure.persistence.models.drupal_rol_model import DrupalRolModel
from src.infrastructure.persistence.models.frontend_module_model import FrontendModuleModel
from src.infrastructure.persistence.models.frontend_module_permission_model import (
    FrontendModulePermissionModel,
)


class SQLAlchemyAutorizacionesRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_roles_async(self) -> list[RolEntity]:
        result = await self._session.execute(
            select(DrupalRolModel).order_by(DrupalRolModel.name.asc())
        )
        return [RolEntity(rid=m.rid, name=(m.name or '').strip()) for m in result.scalars().all()]

    async def obtener_matriz_por_rol_async(self, rid: int) -> list[AutorizacionModuloEntity]:
        stmt = (
            select(FrontendModuleModel, FrontendModulePermissionModel)
            .outerjoin(
                FrontendModulePermissionModel,
                (FrontendModulePermissionModel.module_id == FrontendModuleModel.module_id)
                & (FrontendModulePermissionModel.rid == rid),
            )
            .where(FrontendModuleModel.activo == True)  # noqa: E712
            .order_by(FrontendModuleModel.orden.asc(), FrontendModuleModel.module_id.asc())
        )
        result = await self._session.execute(stmt)
        matriz: list[AutorizacionModuloEntity] = []
        for modulo, permiso in result.all():
            matriz.append(self._to_entity(rid, modulo, permiso))
        return matriz

    async def actualizar_permisos_async(
        self, rid: int, module_id: int, flags: PermisosModulo
    ) -> AutorizacionModuloEntity | None:
        modulo = await self._session.get(FrontendModuleModel, module_id)
        if modulo is None:
            return None
        result = await self._session.execute(
            select(FrontendModulePermissionModel).where(
                (FrontendModulePermissionModel.rid == rid)
                & (FrontendModulePermissionModel.module_id == module_id)
            )
        )
        permiso = result.scalar_one_or_none()
        if permiso is None:
            permiso = FrontendModulePermissionModel(rid=rid, module_id=module_id)
            self._session.add(permiso)
        permiso.puede_ver = flags.puede_ver
        permiso.puede_crear = flags.puede_crear
        permiso.puede_editar = flags.puede_editar
        permiso.puede_eliminar = flags.puede_eliminar
        permiso.puede_exportar = flags.puede_exportar
        permiso.puede_aprobar = flags.puede_aprobar
        await self._session.flush()
        return self._to_entity(rid, modulo, permiso)

    async def actualizar_activo_modulo_async(
        self, module_id: int, activo: bool
    ) -> FrontendModuleModel | None:
        modulo = await self._session.get(FrontendModuleModel, module_id)
        if modulo is None:
            return None
        modulo.activo = activo
        await self._session.flush()
        return modulo

    @staticmethod
    def _to_entity(
        rid: int,
        modulo: FrontendModuleModel,
        permiso: FrontendModulePermissionModel | None,
    ) -> AutorizacionModuloEntity:
        dq = chr(34)
        fallback = dq + 'bi-grid' + dq
        return AutorizacionModuloEntity(
            rid=rid,
            module_id=modulo.module_id,
            module_code=modulo.module_code,
            module_nombre=modulo.nombre,
            module_icono=modulo.icono or 'bi-grid',
            module_activo=bool(modulo.activo),
            permission_id=permiso.permission_id if permiso else 0,
            puede_ver=bool(permiso.puede_ver) if permiso else False,
            puede_crear=bool(permiso.puede_crear) if permiso else False,
            puede_editar=bool(permiso.puede_editar) if permiso else False,
            puede_eliminar=bool(permiso.puede_eliminar) if permiso else False,
            puede_exportar=bool(permiso.puede_exportar) if permiso else False,
            puede_aprobar=bool(permiso.puede_aprobar) if permiso else False,
        )
