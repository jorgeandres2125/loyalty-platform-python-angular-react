from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.comisionista_programa_entity import (
    ComisionistaProgramaEntity,
)
from src.infrastructure.persistence.models.comisionista_programa_model import (
    ComisionistaProgramaModel,
)


class SQLAlchemyAdminProgramaRepo:
    """Adaptador admin de dbo.comisionistas_programa.

    Soporta solo lista + obtener + actualizar nombre (decisión 3).
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_async(self) -> list[ComisionistaProgramaEntity]:
        result = await self._session.execute(
            select(ComisionistaProgramaModel).order_by(
                ComisionistaProgramaModel.cpid.asc()
            )
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def obtener_por_id_async(
        self, cpid: int
    ) -> ComisionistaProgramaEntity | None:
        result = await self._session.execute(
            select(ComisionistaProgramaModel).where(
                ComisionistaProgramaModel.cpid == cpid
            )
        )
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def actualizar_nombre_async(
        self, cpid: int, nuevo_nombre: str
    ) -> ComisionistaProgramaEntity | None:
        result = await self._session.execute(
            select(ComisionistaProgramaModel).where(
                ComisionistaProgramaModel.cpid == cpid
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.cp_nombre = nuevo_nombre
        await self._session.flush()
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: ComisionistaProgramaModel) -> ComisionistaProgramaEntity:
        return ComisionistaProgramaEntity(
            cpid=model.cpid, cp_nombre=(model.cp_nombre or "").strip()
        )
