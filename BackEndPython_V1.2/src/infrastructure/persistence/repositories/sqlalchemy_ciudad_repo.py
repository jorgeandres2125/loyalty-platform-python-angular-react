from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.ciudad_entity import CiudadEntity
from src.infrastructure.persistence.models.ciudad_model import CiudadModel
from src.infrastructure.persistence.models.perfil_contacto_model import (
    PerfilContactoModel,
)

_ZERO: int = 0


class SQLAlchemyCiudadRepo:
    """Adaptador dbo.ciudades. PK `cid` no-identity → MAX(cid)+1.

    Guardia de delete: users_perfil_contacto.ciudad es String(40) y almacena
    el cid como cadena (legado).
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_paginado_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
        did: int | None = None,
    ) -> tuple[list[CiudadEntity], int]:
        offset: int = (page - 1) * page_size
        base = select(CiudadModel)
        if nombre:
            base = base.where(CiudadModel.ciudad.like(f"%{nombre}%"))
        if did is not None:
            base = base.where(CiudadModel.did == did)
        count_result = await self._session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total: int = int(count_result.scalar_one() or 0)
        stmt = base.order_by(CiudadModel.ciudad.asc()).offset(offset).limit(page_size)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def obtener_por_id_async(self, cid: int) -> CiudadEntity | None:
        result = await self._session.execute(
            select(CiudadModel).where(CiudadModel.cid == cid)
        )
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def crear_async(self, entity: CiudadEntity) -> CiudadEntity:
        max_result = await self._session.execute(
            select(func.coalesce(func.max(CiudadModel.cid), _ZERO))
        )
        nuevo_cid: int = int(max_result.scalar_one()) + 1
        model: CiudadModel = CiudadModel(
            cid=nuevo_cid, did=entity.did, ciudad=entity.ciudad
        )
        self._session.add(model)
        await self._session.flush()
        entity.cid = nuevo_cid
        return entity

    async def actualizar_async(
        self, cid: int, entity: CiudadEntity
    ) -> CiudadEntity | None:
        result = await self._session.execute(
            select(CiudadModel).where(CiudadModel.cid == cid)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.did = entity.did
        model.ciudad = entity.ciudad
        await self._session.flush()
        return self._to_entity(model)

    async def eliminar_async(self, cid: int) -> bool:
        result = await self._session.execute(
            delete(CiudadModel).where(CiudadModel.cid == cid)
        )
        await self._session.flush()
        return (result.rowcount or 0) > 0

    async def existe_referenciado_async(self, cid: int) -> bool:
        result = await self._session.execute(
            select(func.count())
            .select_from(PerfilContactoModel)
            .where(PerfilContactoModel.ciudad == str(cid))
        )
        return int(result.scalar_one() or 0) > 0

    @staticmethod
    def _to_entity(model: CiudadModel) -> CiudadEntity:
        return CiudadEntity(
            cid=model.cid,
            did=model.did,
            ciudad=(model.ciudad or "").strip(),
        )
