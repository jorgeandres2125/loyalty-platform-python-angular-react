from __future__ import annotations

from typing import Final

from sqlalchemy import String as SAString
from sqlalchemy import cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity
from src.domain.ports.outbound.cifrador_campos import CifradorCampos
from src.infrastructure.persistence.models.ciudad_model import CiudadModel
from src.infrastructure.persistence.models.comisionista_programa_model import (
    ComisionistaProgramaModel,
)
from src.infrastructure.persistence.models.departamento_model import DepartamentoModel
from src.infrastructure.persistence.models.perfil_contacto_model import PerfilContactoModel
from src.shared.constants.cifrado import TABLA_PERFIL_CONTACTO
from src.shared.utils.cifrado_aad import construir_aad

_CPID_MOVILIDAD: Final[int] = 1


class SQLAlchemyAsesorMovilidadRepo:
    """Adaptador — tabla users_perfil_contacto filtrada por programa Movilidad (cpid=1)."""

    def __init__(self, session: AsyncSession, cipher: CifradorCampos) -> None:
        self._session: AsyncSession = session
        self._cipher: CifradorCampos = cipher

    def _desc(self, valor_enc: bytes | None, columna: str, doc: str) -> str | None:
        return self._cipher.descifrar(
            valor_enc, aad=construir_aad(TABLA_PERFIL_CONTACTO, columna, doc)
        )

    @staticmethod
    def _enriquecido():
        return (
            select(
                PerfilContactoModel,
                ComisionistaProgramaModel.cp_nombre,
                DepartamentoModel.did.label("dep_did"),
                DepartamentoModel.pid.label("dep_pid"),
                DepartamentoModel.departamento.label("dep_nombre"),
                CiudadModel.cid.label("ciu_cid"),
                CiudadModel.did.label("ciu_did"),
                CiudadModel.ciudad.label("ciu_nombre"),
            )
            .join(ComisionistaProgramaModel, PerfilContactoModel.comisionista_programa_id == ComisionistaProgramaModel.cpid)
            .outerjoin(DepartamentoModel, cast(DepartamentoModel.did, SAString) == PerfilContactoModel.departamento)
            .outerjoin(CiudadModel, cast(CiudadModel.cid, SAString) == PerfilContactoModel.ciudad)
            .where(ComisionistaProgramaModel.cpid == _CPID_MOVILIDAD)
        )

    async def listar_async(
        self,
        page: int,
        size: int,
        tipo_doc: str | None = None,
        documento: str | None = None,
    ) -> tuple[list[PerfilContactoEntity], int]:
        offset: int = (page - 1) * size

        count_q = (
            select(func.count())
            .select_from(PerfilContactoModel)
            .join(ComisionistaProgramaModel, PerfilContactoModel.comisionista_programa_id == ComisionistaProgramaModel.cpid)
            .where(ComisionistaProgramaModel.cpid == _CPID_MOVILIDAD)
        )
        if tipo_doc:
            count_q = count_q.where(PerfilContactoModel.tipo_documento == tipo_doc)
        if documento:
            count_q = count_q.where(PerfilContactoModel.numero_documento.like(f"%{documento}%"))

        count_result = await self._session.execute(count_q)
        total: int = count_result.scalar_one()

        stmt = self._enriquecido().order_by(PerfilContactoModel.numero_documento.desc()).offset(offset).limit(size)
        if tipo_doc:
            stmt = stmt.where(PerfilContactoModel.tipo_documento == tipo_doc)
        if documento:
            stmt = stmt.where(PerfilContactoModel.numero_documento.like(f"%{documento}%"))

        result = await self._session.execute(stmt)
        items: list[PerfilContactoEntity] = [
            self._to_entity(model, cp_nombre, dep_did, dep_pid, dep_nombre, ciu_cid, ciu_did, ciu_nombre)
            for model, cp_nombre, dep_did, dep_pid, dep_nombre, ciu_cid, ciu_did, ciu_nombre in result.all()
        ]
        return items, total

    async def obtener_async(self, numero_documento: str) -> PerfilContactoEntity | None:
        stmt = self._enriquecido().where(PerfilContactoModel.numero_documento == numero_documento)
        result = await self._session.execute(stmt)
        row = result.first()
        if row is None:
            return None
        model, cp_nombre, dep_did, dep_pid, dep_nombre, ciu_cid, ciu_did, ciu_nombre = row
        return self._to_entity(model, cp_nombre, dep_did, dep_pid, dep_nombre, ciu_cid, ciu_did, ciu_nombre)

    def _to_entity(
        self,
        model: PerfilContactoModel,
        cp_nombre: str | None,
        dep_did: int | None,
        dep_pid: int | None,
        dep_nombre: str | None,
        ciu_cid: int | None,
        ciu_did: int | None,
        ciu_nombre: str | None,
    ) -> PerfilContactoEntity:
        doc: str = model.numero_documento
        return PerfilContactoEntity(
            numero_documento=model.numero_documento,
            tipo_documento=model.tipo_documento,
            nombre_completo=model.nombre_completo,
            genero=model.genero,
            fecha_nacimiento=model.fecha_nacimiento,
            celular=self._desc(model.celular_enc, "celular", doc),
            telefono=self._desc(model.telefono_enc, "telefono", doc),
            direccion=self._desc(model.direccion_enc, "direccion", doc),
            departamento=model.departamento,
            ciudad=model.ciudad,
            concesionario=model.concesionario,
            tipo_de_cuenta=self._desc(model.tipo_de_cuenta_enc, "tipo_de_cuenta", doc),
            banco=model.banco,
            numero_de_cuenta=self._desc(model.numero_de_cuenta_enc, "numero_de_cuenta", doc),
            acepto_habeas_data=model.acepto_habeas_data,
            comisionista_programa_id=model.comisionista_programa_id,
            comisionista_subprograma_id=model.comisionista_subprograma_id,
            cod_canales=model.cod_canales,
            cod_oficinas=model.cod_oficinas,
            usuario_responsable=model.usuario_responsable,
            estado=model.estado,
            fecha_completado=model.fecha_completado,
            incentivos=model.incentivos,
            cp_nombre=cp_nombre,
            dep_did=dep_did,
            dep_pid=dep_pid,
            dep_nombre=dep_nombre,
            ciu_cid=ciu_cid,
            ciu_did=ciu_did,
            ciu_nombre=ciu_nombre,
        )
