from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.arl_entity import ArlEntity
from src.infrastructure.persistence.models.arl_model import ArlModel
from src.infrastructure.persistence.models.perfil_tributario_model import (
    PerfilTributarioModel,
)

_ZERO: int = 0


class SQLAlchemyArlRepo:
    """Adaptador dbo.arl. PK `tid` no-identity → MAX(tid)+1.
    FK virtual: users_perfil_tributario.arl → arl.tid (guardia de delete)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_paginado_async(
        self, page: int, page_size: int, nombre: str | None = None
    ) -> tuple[list[ArlEntity], int]:
        offset: int = (page - 1) * page_size
        base = select(ArlModel)
        if nombre:
            base = base.where(ArlModel.nombre.like(f"%{nombre}%"))
        count_result = await self._session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total: int = int(count_result.scalar_one() or 0)
        stmt = base.order_by(ArlModel.nombre.asc()).offset(offset).limit(page_size)
        result = await self._session.execute(stmt)
        rows: list[ArlEntity] = [self._to_entity(m) for m in result.scalars().all()]
        return rows, total

    async def obtener_por_id_async(self, tid: int) -> ArlEntity | None:
        result = await self._session.execute(
            select(ArlModel).where(ArlModel.tid == tid)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def crear_async(self, entity: ArlEntity) -> ArlEntity:
        max_result = await self._session.execute(
            select(func.coalesce(func.max(ArlModel.tid), _ZERO))
        )
        nuevo_tid: int = int(max_result.scalar_one()) + 1
        model: ArlModel = ArlModel(tid=nuevo_tid, nombre=entity.nombre, nit=entity.nit)
        self._session.add(model)
        await self._session.flush()
        entity.tid = nuevo_tid
        return entity

    async def actualizar_async(
        self, tid: int, entity: ArlEntity
    ) -> ArlEntity | None:
        result = await self._session.execute(
            select(ArlModel).where(ArlModel.tid == tid)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.nombre = entity.nombre
        model.nit = entity.nit
        await self._session.flush()
        return self._to_entity(model)

    async def eliminar_async(self, tid: int) -> bool:
        result = await self._session.execute(
            delete(ArlModel).where(ArlModel.tid == tid)
        )
        await self._session.flush()
        return (result.rowcount or 0) > 0

    async def existe_referenciado_async(self, tid: int) -> bool:
        result = await self._session.execute(
            select(func.count())
            .select_from(PerfilTributarioModel)
            .where(PerfilTributarioModel.arl == tid)
        )
        return int(result.scalar_one() or 0) > 0

    @staticmethod
    def _to_entity(model: ArlModel) -> ArlEntity:
        return ArlEntity(
            tid=model.tid,
            nombre=(model.nombre or "").strip(),
            nit=(model.nit or None),
        )
