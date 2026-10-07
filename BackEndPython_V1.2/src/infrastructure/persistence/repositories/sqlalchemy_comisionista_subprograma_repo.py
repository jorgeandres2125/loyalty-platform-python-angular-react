from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.comisionista_subprograma_entity import ComisionistaSubprogramaEntity
from src.infrastructure.persistence.models.comisionista_subprograma_model import (
    ComisionistaSubprogramaModel,
)


class SQLAlchemyComisionistaSubprogramaRepo:
    """Adaptador — tabla comisionistas_subprograma."""

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_async(self, cpid: int | None = None) -> list[ComisionistaSubprogramaEntity]:
        stmt = select(ComisionistaSubprogramaModel).order_by(ComisionistaSubprogramaModel.cspid)
        if cpid is not None:
            stmt = stmt.where(ComisionistaSubprogramaModel.cpid == cpid)
        result = await self._session.execute(stmt)
        return [self._to_entity(row) for row in result.scalars().all()]

    async def obtener_async(self, cspid: int) -> ComisionistaSubprogramaEntity | None:
        result = await self._session.execute(
            select(ComisionistaSubprogramaModel).where(ComisionistaSubprogramaModel.cspid == cspid)
        )
        row: ComisionistaSubprogramaModel | None = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def guardar_async(self, entity: ComisionistaSubprogramaEntity) -> ComisionistaSubprogramaEntity:
        result = await self._session.execute(
            select(ComisionistaSubprogramaModel).where(ComisionistaSubprogramaModel.cspid == entity.cspid)
        )
        existing: ComisionistaSubprogramaModel | None = result.scalar_one_or_none()
        if existing:
            existing.cspid_nombre = entity.cspid_nombre
            existing.cpid = entity.cpid
        else:
            existing = ComisionistaSubprogramaModel(
                cspid_nombre=entity.cspid_nombre,
                cpid=entity.cpid,
            )
            self._session.add(existing)
        await self._session.flush()
        await self._session.refresh(existing)
        return self._to_entity(existing)

    @staticmethod
    def _to_entity(model: ComisionistaSubprogramaModel) -> ComisionistaSubprogramaEntity:
        return ComisionistaSubprogramaEntity(
            cspid=model.cspid,
            cspid_nombre=model.cspid_nombre or "",
            cpid=model.cpid,
        )
