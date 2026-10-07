from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.afp_entity import AfpEntity
from src.domain.entities.arl_entity import ArlEntity
from src.domain.entities.banco_entity import BancoEntity
from src.domain.entities.canal_entity import CanalEntity
from src.domain.entities.comisionista_programa_entity import ComisionistaProgramaEntity
from src.domain.entities.comisionista_subprograma_entity import ComisionistaSubprogramaEntity
from src.domain.entities.ejecutivo_catalogo_entity import EjecutivoCatalogoEntity
from src.domain.entities.eps_entity import EpsEntity
from src.domain.entities.oficina_entity import OficinaEntity
from src.domain.entities.profesion_entity import ProfesionEntity
from src.infrastructure.persistence.models.afp_model import AfpModel
from src.infrastructure.persistence.models.arl_model import ArlModel
from src.infrastructure.persistence.models.banco_model import BancoModel
from src.infrastructure.persistence.models.canal_model import CanalModel
from src.infrastructure.persistence.models.canal_oficina_model import CanalOficinaModel
from src.infrastructure.persistence.models.comisionista_programa_model import (
    ComisionistaProgramaModel,
)
from src.infrastructure.persistence.models.comisionista_subprograma_model import (
    ComisionistaSubprogramaModel,
)
from src.infrastructure.persistence.models.ejecutivo_model import EjecutivoCatalogoModel
from src.infrastructure.persistence.models.eps_model import EpsModel
from src.infrastructure.persistence.models.oficina_model import OficinaModel
from src.infrastructure.persistence.models.profesion_model import ProfesionModel


class SQLAlchemyReferenciaRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    @staticmethod
    def _ejecutivo_to_entity(row: EjecutivoCatalogoModel) -> EjecutivoCatalogoEntity:
        return EjecutivoCatalogoEntity(
            usuario_asesor=row.usuario_asesor,
            email_asesor=row.email_asesor or "",
            usuario_comisionista=row.usuario_comisionista or "",
            email_comisionista=row.email_comisionista or "",
            nombre_comisionista=row.nombre_comisionista or "",
            fecha_registro=row.fecha_registro,
        )

    async def listar_ejecutivos_async(self) -> list[EjecutivoCatalogoEntity]:
        result = await self._session.execute(select(EjecutivoCatalogoModel))
        return [self._ejecutivo_to_entity(row) for row in result.scalars().all()]

    async def obtener_ejecutivo_async(self, usuario_asesor: str) -> EjecutivoCatalogoEntity | None:
        # 'Usuario Asesor' no es único (1 asesor : N comisionistas); se toma la
        # primera coincidencia en vez de scalar_one_or_none (que lanzaría con duplicados).
        result = await self._session.execute(
            select(EjecutivoCatalogoModel)
            .where(EjecutivoCatalogoModel.usuario_asesor == usuario_asesor)
            .limit(1)
        )
        row: EjecutivoCatalogoModel | None = result.scalars().first()
        return self._ejecutivo_to_entity(row) if row else None

    async def guardar_ejecutivo_async(self, entity: EjecutivoCatalogoEntity) -> EjecutivoCatalogoEntity:
        model: EjecutivoCatalogoModel = EjecutivoCatalogoModel(
            usuario_asesor=entity.usuario_asesor,
            email_asesor=entity.email_asesor or None,
            usuario_comisionista=entity.usuario_comisionista or None,
            email_comisionista=entity.email_comisionista or None,
            nombre_comisionista=entity.nombre_comisionista or None,
            fecha_registro=entity.fecha_registro,
        )
        self._session.add(model)
        await self._session.flush()
        return entity

    @staticmethod
    def _canal_to_entity(row: CanalModel) -> CanalEntity:
        return CanalEntity(
            cod_canales=row.cod_canales,
            nom_canales=row.nom_canales or "",
            cpid=row.cpid,
            cspid=row.cspid,
            ind_activo=row.ind_activo,
            id_canales=row.id_canales,
        )

    @staticmethod
    def _oficina_to_entity(row: OficinaModel) -> OficinaEntity:
        return OficinaEntity(
            cod_oficinas=row.cod_oficinas,
            id_oficinas=row.id_oficinas,
            nom_oficinas=row.nom_oficinas or "",
            marca=row.marca or "",
            regional=row.regional or "",
            cpid=row.cpid,
            ind_activo=row.ind_activo,
        )

    async def listar_canales_async(self) -> list[CanalEntity]:
        result = await self._session.execute(select(CanalModel))
        return [self._canal_to_entity(row) for row in result.scalars().all()]

    async def listar_canales_filtrados_async(self, cpid: int | None, cspid: int | None) -> list[CanalEntity]:
        stmt = select(CanalModel).where(CanalModel.ind_activo == True)  # noqa: E712
        if cpid is not None:
            stmt = stmt.where(CanalModel.cpid == cpid)
        if cspid is not None:
            stmt = stmt.where(CanalModel.cspid == cspid)
        result = await self._session.execute(stmt)
        return [self._canal_to_entity(row) for row in result.scalars().all()]

    async def listar_canales_por_ciudad_async(self, cid: int) -> list[CanalEntity]:
        stmt = (
            select(CanalModel)
            .join(CanalOficinaModel, CanalModel.cod_canales == CanalOficinaModel.cod_canales)
            .join(OficinaModel, CanalOficinaModel.cod_oficinas == OficinaModel.cod_oficinas)
            .where(OficinaModel.cpid == cid)
            .distinct()
        )
        result = await self._session.execute(stmt)
        return [self._canal_to_entity(row) for row in result.scalars().all()]

    async def listar_oficinas_async(self) -> list[OficinaEntity]:
        result = await self._session.execute(select(OficinaModel))
        return [self._oficina_to_entity(row) for row in result.scalars().all()]

    async def listar_oficinas_filtradas_async(
        self,
        cid: int | None,
        cod_canales: int | None,
        cspid: int | None = None,
    ) -> list[OficinaEntity]:
        stmt = select(OficinaModel).where(OficinaModel.ind_activo == True)  # noqa: E712
        if cod_canales is not None:
            stmt = stmt.join(
                CanalOficinaModel,
                OficinaModel.cod_oficinas == CanalOficinaModel.cod_oficinas,
            ).where(CanalOficinaModel.cod_canales == cod_canales)
            if cspid is not None:
                stmt = stmt.join(
                    CanalModel,
                    CanalOficinaModel.cod_canales == CanalModel.cod_canales,
                ).where(CanalModel.cspid == cspid)
        if cid is not None:
            stmt = stmt.where(OficinaModel.cpid == cid)
        stmt = stmt.distinct()
        result = await self._session.execute(stmt)
        return [self._oficina_to_entity(row) for row in result.scalars().all()]

    @staticmethod
    def _profesion_to_entity(row: ProfesionModel) -> ProfesionEntity:
        return ProfesionEntity(tid=row.tid, nombre=row.nombre)

    async def listar_profesiones_async(self) -> list[ProfesionEntity]:
        result = await self._session.execute(
            select(ProfesionModel).order_by(ProfesionModel.nombre)
        )
        return [self._profesion_to_entity(row) for row in result.scalars().all()]

    @staticmethod
    def _eps_to_entity(row: EpsModel) -> EpsEntity:
        return EpsEntity(tid=row.tid, nombre=row.nombre, nit=row.nit)

    @staticmethod
    def _afp_to_entity(row: AfpModel) -> AfpEntity:
        return AfpEntity(tid=row.tid, nombre=row.nombre, nit=row.nit)

    @staticmethod
    def _arl_to_entity(row: ArlModel) -> ArlEntity:
        return ArlEntity(tid=row.tid, nombre=row.nombre, nit=row.nit)

    async def listar_eps_async(self) -> list[EpsEntity]:
        result = await self._session.execute(select(EpsModel).order_by(EpsModel.nombre))
        return [self._eps_to_entity(row) for row in result.scalars().all()]

    async def listar_afp_async(self) -> list[AfpEntity]:
        result = await self._session.execute(select(AfpModel).order_by(AfpModel.nombre))
        return [self._afp_to_entity(row) for row in result.scalars().all()]

    async def listar_arl_async(self) -> list[ArlEntity]:
        result = await self._session.execute(select(ArlModel).order_by(ArlModel.nombre))
        return [self._arl_to_entity(row) for row in result.scalars().all()]

    @staticmethod
    def _banco_to_entity(row: BancoModel) -> BancoEntity:
        return BancoEntity(tid=row.tid, nombre=row.nombre, codigo=row.codigo)

    async def listar_bancos_async(self) -> list[BancoEntity]:
        result = await self._session.execute(select(BancoModel).order_by(BancoModel.nombre))
        return [self._banco_to_entity(row) for row in result.scalars().all()]

    async def listar_programas_async(self) -> list[ComisionistaProgramaEntity]:
        result = await self._session.execute(
            select(ComisionistaProgramaModel).order_by(ComisionistaProgramaModel.cpid)
        )
        return [
            ComisionistaProgramaEntity(cpid=row.cpid, cp_nombre=row.cp_nombre or "")
            for row in result.scalars().all()
        ]

    async def listar_subprogramas_async(
        self, cpid: int | None = None
    ) -> list[ComisionistaSubprogramaEntity]:
        stmt = select(ComisionistaSubprogramaModel)
        if cpid is not None:
            stmt = stmt.where(ComisionistaSubprogramaModel.cpid == cpid)
        stmt = stmt.order_by(ComisionistaSubprogramaModel.cspid_nombre)
        result = await self._session.execute(stmt)
        return [
            ComisionistaSubprogramaEntity(
                cspid=row.cspid,
                cspid_nombre=row.cspid_nombre or "",
                cpid=row.cpid,
            )
            for row in result.scalars().all()
        ]
