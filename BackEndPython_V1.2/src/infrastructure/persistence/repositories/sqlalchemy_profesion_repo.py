from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.profesion_entity import ProfesionEntity
from src.infrastructure.persistence.models.perfil_emocional_model import (
    PerfilEmocionalModel,
)
from src.infrastructure.persistence.models.profesion_model import ProfesionModel

_ZERO: int = 0


class SQLAlchemyProfesionRepo:
    """Adaptador dbo.taxonomia_profesion. PK `tid` no-identity → MAX(tid)+1.

    Nota sobre FK virtual: users_perfil_emocional.profesion es String(220), no
    almacena `tid` sino el NOMBRE de la profesión. El guardia de delete compara
    por nombre original (el que la fila tiene antes de borrarse).
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_paginado_async(
        self, page: int, page_size: int, nombre: str | None = None
    ) -> tuple[list[ProfesionEntity], int]:
        offset: int = (page - 1) * page_size
        base = select(ProfesionModel)
        if nombre:
            base = base.where(ProfesionModel.nombre.like(f"%{nombre}%"))
        count_result = await self._session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total: int = int(count_result.scalar_one() or 0)
        stmt = base.order_by(ProfesionModel.nombre.asc()).offset(offset).limit(page_size)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def obtener_por_id_async(self, tid: int) -> ProfesionEntity | None:
        result = await self._session.execute(
            select(ProfesionModel).where(ProfesionModel.tid == tid)
        )
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def crear_async(self, entity: ProfesionEntity) -> ProfesionEntity:
        max_result = await self._session.execute(
            select(func.coalesce(func.max(ProfesionModel.tid), _ZERO))
        )
        nuevo_tid: int = int(max_result.scalar_one()) + 1
        model: ProfesionModel = ProfesionModel(tid=nuevo_tid, nombre=entity.nombre)
        self._session.add(model)
        await self._session.flush()
        entity.tid = nuevo_tid
        return entity

    async def actualizar_async(
        self, tid: int, entity: ProfesionEntity
    ) -> ProfesionEntity | None:
        result = await self._session.execute(
            select(ProfesionModel).where(ProfesionModel.tid == tid)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.nombre = entity.nombre
        await self._session.flush()
        return self._to_entity(model)

    async def eliminar_async(self, tid: int) -> bool:
        result = await self._session.execute(
            delete(ProfesionModel).where(ProfesionModel.tid == tid)
        )
        await self._session.flush()
        return (result.rowcount or 0) > 0

    async def existe_referenciado_async(self, tid: int, nombre_original: str) -> bool:
        # Compara por nombre porque la columna en perfil emocional es String, no FK.
        result = await self._session.execute(
            select(func.count())
            .select_from(PerfilEmocionalModel)
            .where(PerfilEmocionalModel.profesion == nombre_original)
        )
        return int(result.scalar_one() or 0) > 0

    @staticmethod
    def _to_entity(model: ProfesionModel) -> ProfesionEntity:
        return ProfesionEntity(tid=model.tid, nombre=(model.nombre or "").strip())
