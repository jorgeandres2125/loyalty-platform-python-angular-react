from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models.canal_oficina_model import CanalOficinaModel


class SQLAlchemyCanalOficinaRepo:
    """Adaptador — tabla canales_oficinas (N:M canal ↔ oficina)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_oficinas_por_canal_async(self, cod_canales: int) -> list[int]:
        stmt = (
            select(CanalOficinaModel.cod_oficinas)
            .where(CanalOficinaModel.cod_canales == cod_canales)
            .where(CanalOficinaModel.cod_oficinas.is_not(None))
            .order_by(CanalOficinaModel.cod_oficinas.asc())
        )
        result = await self._session.execute(stmt)
        return [int(valor) for valor in result.scalars().all() if valor is not None]

    async def reemplazar_oficinas_de_canal_async(
        self, cod_canales: int, cod_oficinas_ids: list[int]
    ) -> None:
        await self._session.execute(
            delete(CanalOficinaModel).where(CanalOficinaModel.cod_canales == cod_canales)
        )
        nuevos: list[CanalOficinaModel] = [
            CanalOficinaModel(cod_canales=cod_canales, cod_oficinas=oid)
            for oid in self._dedup(cod_oficinas_ids)
        ]
        if nuevos:
            self._session.add_all(nuevos)
        await self._session.flush()

    async def listar_canales_por_oficina_async(self, cod_oficinas: int) -> list[int]:
        stmt = (
            select(CanalOficinaModel.cod_canales)
            .where(CanalOficinaModel.cod_oficinas == cod_oficinas)
            .where(CanalOficinaModel.cod_canales.is_not(None))
            .order_by(CanalOficinaModel.cod_canales.asc())
        )
        result = await self._session.execute(stmt)
        return [int(valor) for valor in result.scalars().all() if valor is not None]

    async def reemplazar_canales_de_oficina_async(
        self, cod_oficinas: int, cod_canales_ids: list[int]
    ) -> None:
        await self._session.execute(
            delete(CanalOficinaModel).where(CanalOficinaModel.cod_oficinas == cod_oficinas)
        )
        nuevos: list[CanalOficinaModel] = [
            CanalOficinaModel(cod_canales=cid, cod_oficinas=cod_oficinas)
            for cid in self._dedup(cod_canales_ids)
        ]
        if nuevos:
            self._session.add_all(nuevos)
        await self._session.flush()

    @staticmethod
    def _dedup(ids: list[int]) -> list[int]:
        seen: set[int] = set()
        out: list[int] = []
        for valor in ids:
            if valor not in seen:
                seen.add(valor)
                out.append(valor)
        return out
