from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.banco_entity import BancoEntity
from src.infrastructure.persistence.models.banco_model import BancoModel
from src.infrastructure.persistence.models.perfil_contacto_model import (
    PerfilContactoModel,
)

_ZERO: int = 0


class SQLAlchemyBancoRepo:
    """Adaptador dbo.bancos. PK `tid` no-identity → MAX(tid)+1.
    FK virtual: users_perfil_contacto.banco → bancos.tid."""

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_paginado_async(
        self, page: int, page_size: int, nombre: str | None = None
    ) -> tuple[list[BancoEntity], int]:
        offset: int = (page - 1) * page_size
        base = select(BancoModel)
        if nombre:
            base = base.where(BancoModel.nombre.like(f"%{nombre}%"))
        count_result = await self._session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total: int = int(count_result.scalar_one() or 0)
        stmt = base.order_by(BancoModel.nombre.asc()).offset(offset).limit(page_size)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def obtener_por_id_async(self, tid: int) -> BancoEntity | None:
        result = await self._session.execute(
            select(BancoModel).where(BancoModel.tid == tid)
        )
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def crear_async(self, entity: BancoEntity) -> BancoEntity:
        max_result = await self._session.execute(
            select(func.coalesce(func.max(BancoModel.tid), _ZERO))
        )
        nuevo_tid: int = int(max_result.scalar_one()) + 1
        model: BancoModel = BancoModel(
            tid=nuevo_tid, nombre=entity.nombre, codigo=entity.codigo
        )
        self._session.add(model)
        await self._session.flush()
        entity.tid = nuevo_tid
        return entity

    async def actualizar_async(
        self, tid: int, entity: BancoEntity
    ) -> BancoEntity | None:
        result = await self._session.execute(
            select(BancoModel).where(BancoModel.tid == tid)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.nombre = entity.nombre
        model.codigo = entity.codigo
        await self._session.flush()
        return self._to_entity(model)

    async def eliminar_async(self, tid: int) -> bool:
        result = await self._session.execute(
            delete(BancoModel).where(BancoModel.tid == tid)
        )
        await self._session.flush()
        return (result.rowcount or 0) > 0

    async def existe_referenciado_async(self, tid: int) -> bool:
        result = await self._session.execute(
            select(func.count())
            .select_from(PerfilContactoModel)
            .where(PerfilContactoModel.banco == tid)
        )
        return int(result.scalar_one() or 0) > 0

    @staticmethod
    def _to_entity(model: BancoModel) -> BancoEntity:
        return BancoEntity(
            tid=model.tid,
            nombre=(model.nombre or "").strip(),
            codigo=(model.codigo or None),
        )
