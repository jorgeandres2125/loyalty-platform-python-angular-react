from __future__ import annotations

from typing import Final

from sqlalchemy import String as SAString
from sqlalchemy import cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity
from src.domain.ports.outbound.cifrador_campos import CifradorCampos
from src.infrastructure.persistence.models.canal_model import CanalModel
from src.infrastructure.persistence.models.ciudad_model import CiudadModel
from src.infrastructure.persistence.models.comisionista_programa_model import (
    ComisionistaProgramaModel,
)
from src.infrastructure.persistence.models.comisionista_subprograma_model import (
    ComisionistaSubprogramaModel,
)
from src.infrastructure.persistence.models.departamento_model import DepartamentoModel
from src.infrastructure.persistence.models.oficina_model import OficinaModel
from src.infrastructure.persistence.models.perfil_contacto_model import PerfilContactoModel
from src.shared.constants.cifrado import TABLA_PERFIL_CONTACTO
from src.shared.utils.cifrado_aad import construir_aad

_CPID_CONSUMO: Final[int] = 2


class SQLAlchemyAsesorConsumoRepo:
    """Adaptador — users_perfil_contacto (asesores Consumo, programa_id=2)."""

    def __init__(self, session: AsyncSession, cipher: CifradorCampos) -> None:
        self._session: AsyncSession = session
        self._cipher: CifradorCampos = cipher

    def _desc(self, valor_enc: bytes | None, columna: str, doc: str) -> str | None:
        return self._cipher.descifrar(
            valor_enc, aad=construir_aad(TABLA_PERFIL_CONTACTO, columna, doc)
        )

    async def listar_async(
        self,
        page: int,
        size: int,
        tipo_doc: str | None = None,
        documento: str | None = None,
    ) -> tuple[list[PerfilContactoEntity], int]:
        offset: int = (page - 1) * size

        count_base = (
            select(PerfilContactoModel)
            .join(
                ComisionistaProgramaModel,
                PerfilContactoModel.comisionista_programa_id == ComisionistaProgramaModel.cpid,
            )
            .where(ComisionistaProgramaModel.cpid == _CPID_CONSUMO)
        )
        if tipo_doc:
            count_base = count_base.where(PerfilContactoModel.tipo_documento == tipo_doc)
        if documento:
            count_base = count_base.where(PerfilContactoModel.numero_documento.like(f"%{documento}%"))

        count_result = await self._session.execute(
            select(func.count()).select_from(count_base.subquery())
        )
        total: int = count_result.scalar_one()

        stmt = self._enriquecido()
        if tipo_doc:
            stmt = stmt.where(PerfilContactoModel.tipo_documento == tipo_doc)
        if documento:
            stmt = stmt.where(PerfilContactoModel.numero_documento.like(f"%{documento}%"))
        stmt = stmt.order_by(PerfilContactoModel.numero_documento.desc()).offset(offset).limit(size)

        result = await self._session.execute(stmt)
        items: list[PerfilContactoEntity] = [self._to_entity(*row) for row in result.all()]
        return items, total

    async def obtener_async(self, numero_documento: str) -> PerfilContactoEntity | None:
        stmt = self._enriquecido().where(
            PerfilContactoModel.numero_documento == numero_documento
        )
        result = await self._session.execute(stmt)
        row = result.first()
        return self._to_entity(*row) if row else None

    @staticmethod
    def _enriquecido():
        return (
            select(
                PerfilContactoModel,
                CanalModel.nom_canales,
                OficinaModel.id_oficinas,
                OficinaModel.nom_oficinas,
                ComisionistaProgramaModel.cp_nombre,
                ComisionistaSubprogramaModel.cspid_nombre,
                DepartamentoModel.did.label("dep_did"),
                DepartamentoModel.pid.label("dep_pid"),
                DepartamentoModel.departamento.label("dep_nombre"),
                CiudadModel.cid.label("ciu_cid"),
                CiudadModel.did.label("ciu_did"),
                CiudadModel.ciudad.label("ciu_nombre"),
            )
            .join(
                ComisionistaProgramaModel,
                PerfilContactoModel.comisionista_programa_id == ComisionistaProgramaModel.cpid,
            )
            .outerjoin(
                ComisionistaSubprogramaModel,
                PerfilContactoModel.comisionista_subprograma_id == ComisionistaSubprogramaModel.cspid,
            )
            .outerjoin(CanalModel, PerfilContactoModel.cod_canales == CanalModel.cod_canales)
            .outerjoin(OficinaModel, PerfilContactoModel.cod_oficinas == OficinaModel.cod_oficinas)
            .outerjoin(
                DepartamentoModel,
                cast(DepartamentoModel.did, SAString) == PerfilContactoModel.departamento,
            )
            .outerjoin(
                CiudadModel,
                cast(CiudadModel.cid, SAString) == PerfilContactoModel.ciudad,
            )
            .where(ComisionistaProgramaModel.cpid == _CPID_CONSUMO)
        )

    def _to_entity(
        self,
        perfil: PerfilContactoModel,
        nom_canales: str | None,
        id_oficinas: int | None,
        nom_oficinas: str | None,
        cp_nombre: str | None,
        cspid_nombre: str | None,
        dep_did: int | None,
        dep_pid: int | None,
        dep_nombre: str | None,
        ciu_cid: int | None,
        ciu_did: int | None,
        ciu_nombre: str | None,
    ) -> PerfilContactoEntity:
        doc: str = perfil.numero_documento
        return PerfilContactoEntity(
            numero_documento=perfil.numero_documento,
            tipo_documento=perfil.tipo_documento or "",
            nombre_completo=perfil.nombre_completo or "",
            genero=perfil.genero,
            fecha_nacimiento=perfil.fecha_nacimiento,
            telefono=self._desc(perfil.telefono_enc, "telefono", doc),
            celular=self._desc(perfil.celular_enc, "celular", doc),
            direccion=self._desc(perfil.direccion_enc, "direccion", doc),
            departamento=perfil.departamento,
            ciudad=perfil.ciudad,
            concesionario=perfil.concesionario,
            tipo_de_cuenta=self._desc(perfil.tipo_de_cuenta_enc, "tipo_de_cuenta", doc),
            banco=perfil.banco,
            numero_de_cuenta=self._desc(perfil.numero_de_cuenta_enc, "numero_de_cuenta", doc),
            acepto_habeas_data=perfil.acepto_habeas_data,
            estado=perfil.estado,
            fecha_completado=perfil.fecha_completado,
            cod_canales=perfil.cod_canales,
            cod_oficinas=perfil.cod_oficinas,
            comisionista_programa_id=perfil.comisionista_programa_id,
            comisionista_subprograma_id=perfil.comisionista_subprograma_id,
            requiere_comision=perfil.requiere_comision,
            incentivos=perfil.incentivos,
            usuario_responsable=perfil.usuario_responsable,
            segmentacion=perfil.segmentacion,
            firma_contrato=perfil.firma_contrato,
            motivo_inactivacion=perfil.motivo_inactivacion,
            programa_motivacion=perfil.programa_motivacion,
            email=self._desc(perfil.email_enc, "email", doc),
            nom_canales=nom_canales,
            nom_oficinas=nom_oficinas,
            id_oficinas=id_oficinas,
            cp_nombre=cp_nombre,
            cspid_nombre=cspid_nombre,
            dep_did=dep_did,
            dep_pid=dep_pid,
            dep_nombre=dep_nombre,
            ciu_cid=ciu_cid,
            ciu_did=ciu_did,
            ciu_nombre=ciu_nombre,
        )
