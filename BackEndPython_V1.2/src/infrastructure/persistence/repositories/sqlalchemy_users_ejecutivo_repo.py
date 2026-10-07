from __future__ import annotations

from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.ejecutivo_entity import EjecutivoEntity
from src.infrastructure.persistence.models.ejecutivo_asignacion_model import (
    EjecutivoAsignacionModel,
)


class SQLAlchemyUsersEjecutivoRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_paginado_async(
        self,
        page: int,
        page_size: int,
        tipo_doc: str | None = None,
        documento: str | None = None,
        perfil: str | None = None,
        estado: bool | None = None,
    ) -> tuple[list[EjecutivoEntity], int]:
        params: dict[str, Any] = {}
        filtros: str = ""
        if tipo_doc:
            filtros += " AND LTRIM(RTRIM(tipo_documento)) = :tipo_doc "
            params["tipo_doc"] = tipo_doc.strip()
        if documento:
            filtros += " AND numero_documento LIKE :documento "
            params["documento"] = f"%{documento}%"
        if perfil is not None:
            filtros += " AND perfil = :perfil "
            params["perfil"] = perfil
        if estado is not None:
            filtros += " AND estado = :estado "
            params["estado"] = 1 if estado else 0

        sql_count: str = f"SELECT COUNT(*) FROM dbo.users_ejecutivos WHERE 1=1{filtros}"
        total_res = await self._session.execute(text(sql_count), params)
        total: int = int(total_res.scalar_one() or 0)

        offset: int = (page - 1) * page_size
        params_page: dict[str, Any] = {**params, "_off": offset, "_ps": page_size}
        sql_page: str = (
            "SELECT id, tipo_documento, numero_documento, nombre_completo, "
            "codigo_ejecutivo, celular, perfil, email, estado "
            "FROM dbo.users_ejecutivos "
            f"WHERE 1=1{filtros}"
            "ORDER BY id DESC "
            "OFFSET :_off ROWS FETCH NEXT :_ps ROWS ONLY"
        )
        res = await self._session.execute(text(sql_page), params_page)
        rows: list[EjecutivoEntity] = [
            EjecutivoEntity(
                id=int(row[0]),
                tipo_documento=(row[1] or "").strip() if row[1] else "",
                numero_documento=(row[2] or "").strip(),
                nombre_completo=row[3] or "",
                codigo_ejecutivo=row[4] or "",
                celular=row[5] or "",
                perfil=row[6] or "",
                email=row[7] or "",
                estado=bool(row[8]),
            )
            for row in res.fetchall()
        ]
        return rows, total

    async def obtener_por_id_async(self, ejecutivo_id: int) -> EjecutivoEntity | None:
        result = await self._session.execute(
            select(EjecutivoAsignacionModel).where(EjecutivoAsignacionModel.id == ejecutivo_id)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def obtener_por_numero_documento_async(
        self, numero_documento: str
    ) -> EjecutivoEntity | None:
        result = await self._session.execute(
            select(EjecutivoAsignacionModel).where(
                EjecutivoAsignacionModel.numero_documento == numero_documento
            )
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def crear_async(self, entity: EjecutivoEntity) -> EjecutivoEntity:
        model: EjecutivoAsignacionModel = EjecutivoAsignacionModel(
            tipo_documento=entity.tipo_documento or None,
            numero_documento=entity.numero_documento,
            nombre_completo=entity.nombre_completo or None,
            codigo_ejecutivo=entity.codigo_ejecutivo or None,
            celular=entity.celular or None,
            perfil=entity.perfil or None,
            email=entity.email or None,
            estado=entity.estado,
        )
        self._session.add(model)
        await self._session.flush()
        entity.id = model.id
        return entity

    async def actualizar_async(
        self, ejecutivo_id: int, entity: EjecutivoEntity
    ) -> EjecutivoEntity | None:
        result = await self._session.execute(
            select(EjecutivoAsignacionModel).where(EjecutivoAsignacionModel.id == ejecutivo_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.tipo_documento = entity.tipo_documento or None
        model.numero_documento = entity.numero_documento
        model.nombre_completo = entity.nombre_completo or None
        model.codigo_ejecutivo = entity.codigo_ejecutivo or None
        model.celular = entity.celular or None
        model.perfil = entity.perfil or None
        model.email = entity.email or None
        model.estado = entity.estado
        await self._session.flush()
        return self._to_entity(model)

    @staticmethod
    def _to_entity(row: EjecutivoAsignacionModel) -> EjecutivoEntity:
        return EjecutivoEntity(
            id=row.id,
            tipo_documento=(row.tipo_documento or "").strip() if row.tipo_documento else "",
            numero_documento=(row.numero_documento or "").strip(),
            nombre_completo=row.nombre_completo or "",
            codigo_ejecutivo=row.codigo_ejecutivo or "",
            celular=row.celular or "",
            perfil=row.perfil or "",
            email=row.email or "",
            estado=bool(row.estado),
        )
