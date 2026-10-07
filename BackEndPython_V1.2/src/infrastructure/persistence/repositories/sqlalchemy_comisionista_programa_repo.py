from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.comisionista_programa_entity import ComisionistaProgramaEntity
from src.infrastructure.persistence.models.comisionista_programa_model import (
    ComisionistaProgramaModel,
)


class SQLAlchemyComisionistaProgramaRepo:
    """Adaptador — tabla comisionistas_programa."""

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_async(self) -> list[ComisionistaProgramaEntity]:
        result = await self._session.execute(
            select(ComisionistaProgramaModel).order_by(ComisionistaProgramaModel.cpid)
        )
        return [self._to_entity(row) for row in result.scalars().all()]

    async def obtener_async(self, cpid: int) -> ComisionistaProgramaEntity | None:
        result = await self._session.execute(
            select(ComisionistaProgramaModel).where(ComisionistaProgramaModel.cpid == cpid)
        )
        row: ComisionistaProgramaModel | None = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def guardar_async(self, entity: ComisionistaProgramaEntity) -> ComisionistaProgramaEntity:
        result = await self._session.execute(
            select(ComisionistaProgramaModel).where(ComisionistaProgramaModel.cpid == entity.cpid)
        )
        existing: ComisionistaProgramaModel | None = result.scalar_one_or_none()
        if existing:
            existing.cp_nombre = entity.cp_nombre
        else:
            existing = ComisionistaProgramaModel(cpid=entity.cpid, cp_nombre=entity.cp_nombre)
            self._session.add(existing)
        await self._session.flush()
        await self._session.refresh(existing)
        return self._to_entity(existing)

    @staticmethod
    def _to_entity(model: ComisionistaProgramaModel) -> ComisionistaProgramaEntity:
        return ComisionistaProgramaEntity(cpid=model.cpid, cp_nombre=model.cp_nombre or "")
