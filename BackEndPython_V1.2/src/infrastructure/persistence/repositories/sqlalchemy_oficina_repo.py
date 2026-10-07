from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.oficina_entity import OficinaEntity
from src.infrastructure.persistence.models.ciudad_model import CiudadModel
from src.infrastructure.persistence.models.departamento_model import DepartamentoModel
from src.infrastructure.persistence.models.oficina_model import OficinaModel

_ZERO: int = 0


class SQLAlchemyOficinaRepo:
    """Adaptador — tabla oficinas (admin CRUD)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_paginado_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
        marca: str | None = None,
        regional: str | None = None,
        ind_activo: bool | None = None,
    ) -> tuple[list[OficinaEntity], int]:
        offset: int = (page - 1) * page_size

        conditions = []
        if nombre:
            conditions.append(OficinaModel.nom_oficinas.like(f"%{nombre}%"))
        if marca:
            conditions.append(OficinaModel.marca.like(f"%{marca}%"))
        if regional:
            conditions.append(OficinaModel.regional.like(f"%{regional}%"))
        if ind_activo is not None:
            conditions.append(OficinaModel.ind_activo == ind_activo)

        count_stmt = select(func.count(OficinaModel.cod_oficinas))
        for condicion in conditions:
            count_stmt = count_stmt.where(condicion)
        count_result = await self._session.execute(count_stmt)
        total: int = int(count_result.scalar_one() or 0)

        stmt = (
            select(
                OficinaModel,
                CiudadModel.ciudad.label("ciu_nombre"),
                CiudadModel.did.label("ciu_did"),
                DepartamentoModel.departamento.label("dep_nombre"),
            )
            .outerjoin(CiudadModel, CiudadModel.cid == OficinaModel.cpid)
            .outerjoin(DepartamentoModel, DepartamentoModel.did == CiudadModel.did)
        )
        for condicion in conditions:
            stmt = stmt.where(condicion)
        stmt = stmt.order_by(OficinaModel.cod_oficinas.desc()).offset(offset).limit(page_size)

        result = await self._session.execute(stmt)
        rows: list[OficinaEntity] = [self._row_to_entity(row) for row in result.all()]
        return rows, total

    async def listar_activas_async(self) -> list[OficinaEntity]:
        stmt = (
            select(OficinaModel)
            .where(OficinaModel.ind_activo == True)  # noqa: E712
            .order_by(OficinaModel.nom_oficinas.asc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def obtener_por_id_async(self, cod_oficinas: int) -> OficinaEntity | None:
        stmt = (
            select(
                OficinaModel,
                CiudadModel.ciudad.label("ciu_nombre"),
                CiudadModel.did.label("ciu_did"),
                DepartamentoModel.departamento.label("dep_nombre"),
            )
            .outerjoin(CiudadModel, CiudadModel.cid == OficinaModel.cpid)
            .outerjoin(DepartamentoModel, DepartamentoModel.did == CiudadModel.did)
            .where(OficinaModel.cod_oficinas == cod_oficinas)
        )
        result = await self._session.execute(stmt)
        row = result.one_or_none()
        return self._row_to_entity(row) if row else None

    async def crear_async(self, entity: OficinaEntity) -> OficinaEntity:
        max_result = await self._session.execute(
            select(func.coalesce(func.max(OficinaModel.id_oficinas), _ZERO))
        )
        entity.id_oficinas = int(max_result.scalar_one()) + 1
        model: OficinaModel = OficinaModel(
            id_oficinas=entity.id_oficinas,
            nom_oficinas=entity.nom_oficinas or None,
            marca=entity.marca or None,
            regional=entity.regional or None,
            cpid=entity.cpid,
            ind_activo=entity.ind_activo,
        )
        self._session.add(model)
        await self._session.flush()
        entity.cod_oficinas = model.cod_oficinas
        return entity

    async def actualizar_async(
        self, cod_oficinas: int, entity: OficinaEntity
    ) -> OficinaEntity | None:
        result = await self._session.execute(
            select(OficinaModel).where(OficinaModel.cod_oficinas == cod_oficinas)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        # id_oficinas es inmutable tras la creación — no se sobreescribe
        model.nom_oficinas = entity.nom_oficinas or None
        model.marca = entity.marca or None
        model.regional = entity.regional or None
        model.cpid = entity.cpid
        model.ind_activo = entity.ind_activo
        await self._session.flush()
        return self._to_entity(model)

    @staticmethod
    def _row_to_entity(row: object) -> OficinaEntity:
        """Convierte fila de consulta con JOIN ciudad/departamento."""
        model: OficinaModel = row[0]  # type: ignore[index]
        return OficinaEntity(
            cod_oficinas=model.cod_oficinas,
            id_oficinas=model.id_oficinas,
            nom_oficinas=(model.nom_oficinas or "").strip(),
            marca=(model.marca or "").strip(),
            regional=(model.regional or "").strip(),
            cpid=model.cpid,
            ind_activo=model.ind_activo,
            ciudad_nombre=row[1] or "",  # type: ignore[index]
            did=row[2],                  # type: ignore[index]
            departamento_nombre=row[3] or "",  # type: ignore[index]
        )

    @staticmethod
    def _to_entity(model: OficinaModel) -> OficinaEntity:
        """Convierte modelo sin JOIN (usar solo tras crear/actualizar)."""
        return OficinaEntity(
            cod_oficinas=model.cod_oficinas,
            id_oficinas=model.id_oficinas,
            nom_oficinas=(model.nom_oficinas or "").strip(),
            marca=(model.marca or "").strip(),
            regional=(model.regional or "").strip(),
            cpid=model.cpid,
            ind_activo=model.ind_activo,
        )
