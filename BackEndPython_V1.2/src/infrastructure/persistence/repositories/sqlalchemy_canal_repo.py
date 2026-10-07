from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.canal_entity import CanalEntity
from src.infrastructure.persistence.models.canal_model import CanalModel

_ZERO: int = 0


class SQLAlchemyCanalRepo:
    """Adaptador — tabla canales (admin CRUD)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_paginado_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
        ind_activo: bool | None = None,
    ) -> tuple[list[CanalEntity], int]:
        offset: int = (page - 1) * page_size

        base = select(CanalModel)
        if nombre:
            base = base.where(CanalModel.nom_canales.like(f"%{nombre}%"))
        if ind_activo is not None:
            base = base.where(CanalModel.ind_activo == ind_activo)

        count_result = await self._session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total: int = int(count_result.scalar_one() or 0)

        stmt = base.order_by(CanalModel.cod_canales.desc()).offset(offset).limit(page_size)
        result = await self._session.execute(stmt)
        rows: list[CanalEntity] = [self._to_entity(model) for model in result.scalars().all()]
        return rows, total

    async def listar_activas_async(self) -> list[CanalEntity]:
        stmt = (
            select(CanalModel)
            .where(CanalModel.ind_activo == True)  # noqa: E712
            .order_by(CanalModel.nom_canales.asc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def obtener_por_id_async(self, cod_canales: int) -> CanalEntity | None:
        result = await self._session.execute(
            select(CanalModel).where(CanalModel.cod_canales == cod_canales)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def crear_async(self, entity: CanalEntity) -> CanalEntity:
        max_result = await self._session.execute(
            select(func.coalesce(func.max(CanalModel.id_canales), _ZERO))
        )
        entity.id_canales = int(max_result.scalar_one()) + 1
        model: CanalModel = CanalModel(
            nom_canales=entity.nom_canales or None,
            cpid=entity.cpid,
            cspid=entity.cspid,
            ind_activo=entity.ind_activo,
            id_canales=entity.id_canales,
        )
        self._session.add(model)
        await self._session.flush()
        entity.cod_canales = model.cod_canales
        return entity

    async def actualizar_async(
        self, cod_canales: int, entity: CanalEntity
    ) -> CanalEntity | None:
        result = await self._session.execute(
            select(CanalModel).where(CanalModel.cod_canales == cod_canales)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.nom_canales = entity.nom_canales or None
        model.cpid = entity.cpid
        model.cspid = entity.cspid
        model.ind_activo = entity.ind_activo
        # id_canales is immutable after creation — do not overwrite
        await self._session.flush()
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: CanalModel) -> CanalEntity:
        return CanalEntity(
            cod_canales=model.cod_canales,
            nom_canales=(model.nom_canales or "").strip(),
            cpid=model.cpid,
            cspid=model.cspid,
            ind_activo=model.ind_activo,
            id_canales=model.id_canales,
        )

