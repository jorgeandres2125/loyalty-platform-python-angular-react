from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.comisionista_subprograma_entity import (
    ComisionistaSubprogramaEntity,
)
from src.infrastructure.persistence.models.canal_model import CanalModel
from src.infrastructure.persistence.models.comisionista_subprograma_model import (
    ComisionistaSubprogramaModel,
)


class SQLAlchemyAdminSubprogramaRepo:
    """Adaptador admin de dbo.comisionistas_subprograma.

    Es la ÚNICA tabla del Panel de Control con IDENTITY real (cspid). El INSERT
    NO setea cspid; SQLAlchemy / SQL Server lo autoasignan.
    FK virtual: canales.cspid → comisionistas_subprograma.cspid.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_paginado_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
        cpid: int | None = None,
    ) -> tuple[list[ComisionistaSubprogramaEntity], int]:
        offset: int = (page - 1) * page_size
        base = select(ComisionistaSubprogramaModel)
        if nombre:
            base = base.where(
                ComisionistaSubprogramaModel.cspid_nombre.like(f"%{nombre}%")
            )
        if cpid is not None:
            base = base.where(ComisionistaSubprogramaModel.cpid == cpid)
        count_result = await self._session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total: int = int(count_result.scalar_one() or 0)
        stmt = (
            base.order_by(ComisionistaSubprogramaModel.cspid_nombre.asc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def obtener_por_id_async(
        self, cspid: int
    ) -> ComisionistaSubprogramaEntity | None:
        result = await self._session.execute(
            select(ComisionistaSubprogramaModel).where(
                ComisionistaSubprogramaModel.cspid == cspid
            )
        )
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def crear_async(
        self, entity: ComisionistaSubprogramaEntity
    ) -> ComisionistaSubprogramaEntity:
        # cspid es IDENTITY → no se asigna manualmente.
        model: ComisionistaSubprogramaModel = ComisionistaSubprogramaModel(
            cspid_nombre=entity.cspid_nombre, cpid=entity.cpid
        )
        self._session.add(model)
        await self._session.flush()
        entity.cspid = model.cspid
        return entity

    async def actualizar_async(
        self, cspid: int, entity: ComisionistaSubprogramaEntity
    ) -> ComisionistaSubprogramaEntity | None:
        result = await self._session.execute(
            select(ComisionistaSubprogramaModel).where(
                ComisionistaSubprogramaModel.cspid == cspid
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.cspid_nombre = entity.cspid_nombre
        model.cpid = entity.cpid
        await self._session.flush()
        return self._to_entity(model)

    async def eliminar_async(self, cspid: int) -> bool:
        result = await self._session.execute(
            delete(ComisionistaSubprogramaModel).where(
                ComisionistaSubprogramaModel.cspid == cspid
            )
        )
        await self._session.flush()
        return (result.rowcount or 0) > 0

    async def existe_referenciado_async(self, cspid: int) -> bool:
        result = await self._session.execute(
            select(func.count())
            .select_from(CanalModel)
            .where(CanalModel.cspid == cspid)
        )
        return int(result.scalar_one() or 0) > 0

    @staticmethod
    def _to_entity(
        model: ComisionistaSubprogramaModel,
    ) -> ComisionistaSubprogramaEntity:
        return ComisionistaSubprogramaEntity(
            cspid=model.cspid,
            cspid_nombre=(model.cspid_nombre or "").strip(),
            cpid=model.cpid,
        )
