from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.afp_entity import AfpEntity
from src.infrastructure.persistence.models.afp_model import AfpModel
from src.infrastructure.persistence.models.perfil_tributario_model import (
    PerfilTributarioModel,
)

_ZERO: int = 0


class SQLAlchemyAfpRepo:
    """Adaptador para dbo.afp.

    PK `tid` no es IDENTITY → la generación de nuevos códigos sigue la
    política 2A (`MAX(tid)+1`). FK virtual: `users_perfil_tributario.afp`
    referencia `afp.tid`; el método `existe_referenciado_async` consulta
    esa relación para bloquear deletes que romperían integridad.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_paginado_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
    ) -> tuple[list[AfpEntity], int]:
        offset: int = (page - 1) * page_size
        base = select(AfpModel)
        if nombre:
            base = base.where(AfpModel.nombre.like(f"%{nombre}%"))

        count_result = await self._session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total: int = int(count_result.scalar_one() or 0)

        stmt = base.order_by(AfpModel.nombre.asc()).offset(offset).limit(page_size)
        result = await self._session.execute(stmt)
        rows: list[AfpEntity] = [
            self._to_entity(model) for model in result.scalars().all()
        ]
        return rows, total

    async def listar_todos_async(self) -> list[AfpEntity]:
        stmt = select(AfpModel).order_by(AfpModel.nombre.asc())
        result = await self._session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def obtener_por_id_async(self, tid: int) -> AfpEntity | None:
        result = await self._session.execute(
            select(AfpModel).where(AfpModel.tid == tid)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def crear_async(self, entity: AfpEntity) -> AfpEntity:
        max_result = await self._session.execute(
            select(func.coalesce(func.max(AfpModel.tid), _ZERO))
        )
        nuevo_tid: int = int(max_result.scalar_one()) + 1
        model: AfpModel = AfpModel(
            tid=nuevo_tid,
            nombre=entity.nombre,
            nit=entity.nit,
        )
        self._session.add(model)
        await self._session.flush()
        entity.tid = nuevo_tid
        return entity

    async def actualizar_async(
        self, tid: int, entity: AfpEntity
    ) -> AfpEntity | None:
        result = await self._session.execute(
            select(AfpModel).where(AfpModel.tid == tid)
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
            delete(AfpModel).where(AfpModel.tid == tid)
        )
        await self._session.flush()
        return (result.rowcount or 0) > 0

    async def existe_referenciado_async(self, tid: int) -> bool:
        result = await self._session.execute(
            select(func.count())
            .select_from(PerfilTributarioModel)
            .where(PerfilTributarioModel.afp == tid)
        )
        total: int = int(result.scalar_one() or 0)
        return total > 0

    @staticmethod
    def _to_entity(model: AfpModel) -> AfpEntity:
        return AfpEntity(
            tid=model.tid,
            nombre=(model.nombre or "").strip(),
            nit=(model.nit or None),
        )
