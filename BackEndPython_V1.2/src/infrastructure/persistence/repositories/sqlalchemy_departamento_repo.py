from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.departamento_entity import DepartamentoEntity
from src.infrastructure.persistence.models.ciudad_model import CiudadModel
from src.infrastructure.persistence.models.departamento_model import DepartamentoModel
from src.infrastructure.persistence.models.perfil_contacto_model import (
    PerfilContactoModel,
)

_ZERO: int = 0


class SQLAlchemyDepartamentoRepo:
    """Adaptador dbo.departamentos. PK `did` no-identity → MAX(did)+1.

    Guardia de delete: dos checks
      1. ciudades.did = :did (hay ciudades hijas)
      2. users_perfil_contacto.departamento = str(:did) (la columna es String(40)
         pero almacena el did como cadena — el JSON viene del legacy así).
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_paginado_async(
        self, page: int, page_size: int, nombre: str | None = None
    ) -> tuple[list[DepartamentoEntity], int]:
        offset: int = (page - 1) * page_size
        base = select(DepartamentoModel)
        if nombre:
            base = base.where(DepartamentoModel.departamento.like(f"%{nombre}%"))
        count_result = await self._session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total: int = int(count_result.scalar_one() or 0)
        stmt = (
            base.order_by(DepartamentoModel.departamento.asc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def obtener_por_id_async(self, did: int) -> DepartamentoEntity | None:
        result = await self._session.execute(
            select(DepartamentoModel).where(DepartamentoModel.did == did)
        )
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def crear_async(self, entity: DepartamentoEntity) -> DepartamentoEntity:
        max_result = await self._session.execute(
            select(func.coalesce(func.max(DepartamentoModel.did), _ZERO))
        )
        nuevo_did: int = int(max_result.scalar_one()) + 1
        model: DepartamentoModel = DepartamentoModel(
            did=nuevo_did, pid=entity.pid, departamento=entity.departamento
        )
        self._session.add(model)
        await self._session.flush()
        entity.did = nuevo_did
        return entity

    async def actualizar_async(
        self, did: int, entity: DepartamentoEntity
    ) -> DepartamentoEntity | None:
        result = await self._session.execute(
            select(DepartamentoModel).where(DepartamentoModel.did == did)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.pid = entity.pid
        model.departamento = entity.departamento
        await self._session.flush()
        return self._to_entity(model)

    async def eliminar_async(self, did: int) -> bool:
        result = await self._session.execute(
            delete(DepartamentoModel).where(DepartamentoModel.did == did)
        )
        await self._session.flush()
        return (result.rowcount or 0) > 0

    async def existe_referenciado_async(self, did: int) -> bool:
        # Check 1: ¿hay ciudades hijas?
        ciudades_result = await self._session.execute(
            select(func.count())
            .select_from(CiudadModel)
            .where(CiudadModel.did == did)
        )
        if int(ciudades_result.scalar_one() or 0) > 0:
            return True
        # Check 2: ¿hay perfiles con este departamento? (la columna es String)
        perfiles_result = await self._session.execute(
            select(func.count())
            .select_from(PerfilContactoModel)
            .where(PerfilContactoModel.departamento == str(did))
        )
        return int(perfiles_result.scalar_one() or 0) > 0

    @staticmethod
    def _to_entity(model: DepartamentoModel) -> DepartamentoEntity:
        return DepartamentoEntity(
            did=model.did,
            pid=model.pid,
            departamento=(model.departamento or "").strip(),
        )
