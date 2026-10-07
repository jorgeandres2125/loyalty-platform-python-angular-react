from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.rol_asignado_entity import RolAsignadoEntity
from src.domain.entities.rol_entity import RolEntity
from src.domain.entities.usuario_cuenta_entity import UsuarioCuentaEntity
from src.infrastructure.persistence.models.drupal_rol_model import DrupalRolModel
from src.infrastructure.persistence.models.drupal_user_model import DrupalUserModel
from src.infrastructure.persistence.models.drupal_user_rol_model import DrupalUserRolModel

# rid 1 = anónimo, rid 2 = autenticado: roles implícitos de Drupal, no asignables.
_ROLES_TECNICOS: tuple[int, ...] = (1, 2)


class SQLAlchemyAsignacionRolesRepo:
    """Adaptador de asignación de roles (AP-0054) sobre el modelo Drupal:
    dbo.role, dbo.users y la tabla puente dbo.users_roles."""

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_roles_asignables_async(self) -> list[RolEntity]:
        result = await self._session.execute(
            select(DrupalRolModel)
            .where(DrupalRolModel.rid.notin_(_ROLES_TECNICOS))
            .order_by(DrupalRolModel.name.asc())
        )
        return [RolEntity(rid=m.rid, name=(m.name or "").strip()) for m in result.scalars().all()]

    async def existe_rol_async(self, rid: int) -> bool:
        result = await self._session.execute(
            select(DrupalRolModel.rid).where(DrupalRolModel.rid == rid)
        )
        return result.scalar_one_or_none() is not None

    async def obtener_nombre_rol_async(self, rid: int) -> str | None:
        result = await self._session.execute(
            select(DrupalRolModel.name).where(DrupalRolModel.rid == rid)
        )
        nombre: str | None = result.scalar_one_or_none()
        return nombre.strip() if nombre else None

    async def obtener_usuario_async(self, uid: int) -> UsuarioCuentaEntity | None:
        result = await self._session.execute(
            select(DrupalUserModel).where(DrupalUserModel.uid == uid)
        )
        row = result.scalar_one_or_none()
        return self._to_cuenta(row) if row else None

    async def listar_usuarios_de_rol_async(
        self, rid: int, texto: str | None, page: int, page_size: int
    ) -> tuple[list[UsuarioCuentaEntity], int]:
        base: Select[tuple[DrupalUserModel]] = (
            select(DrupalUserModel)
            .join(DrupalUserRolModel, DrupalUserRolModel.uid == DrupalUserModel.uid)
            .where(DrupalUserRolModel.rid == rid, DrupalUserModel.uid > 1)
        )
        return await self._paginar(self._aplicar_texto(base, texto), page, page_size)

    async def buscar_usuarios_async(
        self, texto: str | None, page: int, page_size: int
    ) -> tuple[list[UsuarioCuentaEntity], int]:
        base: Select[tuple[DrupalUserModel]] = select(DrupalUserModel).where(
            DrupalUserModel.uid > 1
        )
        return await self._paginar(self._aplicar_texto(base, texto), page, page_size)

    async def obtener_roles_de_usuario_async(self, uid: int) -> list[RolAsignadoEntity]:
        asignados_res = await self._session.execute(
            select(DrupalUserRolModel.rid).where(DrupalUserRolModel.uid == uid)
        )
        asignados: set[int] = set(asignados_res.scalars().all())
        roles_res = await self._session.execute(
            select(DrupalRolModel)
            .where(DrupalRolModel.rid.notin_(_ROLES_TECNICOS))
            .order_by(DrupalRolModel.name.asc())
        )
        return [
            RolAsignadoEntity(rid=m.rid, name=(m.name or "").strip(), asignado=m.rid in asignados)
            for m in roles_res.scalars().all()
        ]

    async def asignar_rol_async(self, uid: int, rid: int) -> bool:
        existe = await self._session.execute(
            select(DrupalUserRolModel).where(
                DrupalUserRolModel.uid == uid, DrupalUserRolModel.rid == rid
            )
        )
        if existe.scalar_one_or_none() is not None:
            return False
        self._session.add(DrupalUserRolModel(uid=uid, rid=rid))
        await self._session.flush()
        return True

    async def quitar_rol_async(self, uid: int, rid: int) -> bool:
        res = await self._session.execute(
            select(DrupalUserRolModel).where(
                DrupalUserRolModel.uid == uid, DrupalUserRolModel.rid == rid
            )
        )
        obj = res.scalar_one_or_none()
        if obj is None:
            return False
        await self._session.delete(obj)
        await self._session.flush()
        return True

    @staticmethod
    def _aplicar_texto(
        stmt: Select[tuple[DrupalUserModel]], texto: str | None
    ) -> Select[tuple[DrupalUserModel]]:
        if texto and texto.strip():
            patron: str = f"%{texto.strip()}%"
            stmt = stmt.where(
                or_(DrupalUserModel.name.like(patron), DrupalUserModel.mail.like(patron))
            )
        return stmt

    async def _paginar(
        self, base: Select[tuple[DrupalUserModel]], page: int, page_size: int
    ) -> tuple[list[UsuarioCuentaEntity], int]:
        total: int = (
            await self._session.execute(select(func.count()).select_from(base.subquery()))
        ).scalar_one()
        stmt = base.order_by(DrupalUserModel.name).offset((page - 1) * page_size).limit(page_size)
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_cuenta(r) for r in rows], total

    @staticmethod
    def _to_cuenta(model: DrupalUserModel) -> UsuarioCuentaEntity:
        return UsuarioCuentaEntity(
            uid=model.uid,
            nombre=model.name or "",
            email=model.mail or "",
            activo=(model.status == 1),
        )
