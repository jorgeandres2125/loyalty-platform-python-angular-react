from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.eps_entity import EpsEntity
from src.infrastructure.persistence.models.eps_model import EpsModel
from src.infrastructure.persistence.models.perfil_tributario_model import (
    PerfilTributarioModel,
)

_ZERO: int = 0


class SQLAlchemyEpsRepo:
    """Adaptador dbo.eps. PK `tid` no-identity → MAX(tid)+1.
    FK virtual: users_perfil_tributario.eps → eps.tid."""

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_paginado_async(
        self, page: int, page_size: int, nombre: str | None = None
    ) -> tuple[list[EpsEntity], int]:
        offset: int = (page - 1) * page_size
        base = select(EpsModel)
        if nombre:
            base = base.where(EpsModel.nombre.like(f"%{nombre}%"))
        count_result = await self._session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total: int = int(count_result.scalar_one() or 0)
        stmt = base.order_by(EpsModel.nombre.asc()).offset(offset).limit(page_size)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def obtener_por_id_async(self, tid: int) -> EpsEntity | None:
        result = await self._session.execute(select(EpsModel).where(EpsModel.tid == tid))
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def crear_async(self, entity: EpsEntity) -> EpsEntity:
        max_result = await self._session.execute(
            select(func.coalesce(func.max(EpsModel.tid), _ZERO))
        )
        nuevo_tid: int = int(max_result.scalar_one()) + 1
        model: EpsModel = EpsModel(tid=nuevo_tid, nombre=entity.nombre, nit=entity.nit)
        self._session.add(model)
        await self._session.flush()
        entity.tid = nuevo_tid
        return entity

    async def actualizar_async(self, tid: int, entity: EpsEntity) -> EpsEntity | None:
        result = await self._session.execute(select(EpsModel).where(EpsModel.tid == tid))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.nombre = entity.nombre
        model.nit = entity.nit
        await self._session.flush()
        return self._to_entity(model)

    async def eliminar_async(self, tid: int) -> bool:
        result = await self._session.execute(delete(EpsModel).where(EpsModel.tid == tid))
        await self._session.flush()
        return (result.rowcount or 0) > 0

    async def existe_referenciado_async(self, tid: int) -> bool:
        result = await self._session.execute(
            select(func.count())
            .select_from(PerfilTributarioModel)
            .where(PerfilTributarioModel.eps == tid)
        )
        return int(result.scalar_one() or 0) > 0

    @staticmethod
    def _to_entity(model: EpsModel) -> EpsEntity:
        return EpsEntity(
            tid=model.tid, nombre=(model.nombre or "").strip(), nit=(model.nit or None)
        )
