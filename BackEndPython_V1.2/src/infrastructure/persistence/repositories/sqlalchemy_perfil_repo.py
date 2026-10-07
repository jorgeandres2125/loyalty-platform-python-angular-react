from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.comisionista_programa_entity import ComisionistaProgramaEntity
from src.domain.entities.comisionista_subprograma_entity import ComisionistaSubprogramaEntity
from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity
from src.domain.entities.perfil_emocional_entity import PerfilEmocionalEntity
from src.domain.entities.perfil_tributario_entity import PerfilTributarioEntity
from src.domain.ports.outbound.cifrador_campos import CifradorCampos
from src.infrastructure.persistence.models.comisionista_programa_model import (
    ComisionistaProgramaModel,
)
from src.infrastructure.persistence.models.comisionista_subprograma_model import (
    ComisionistaSubprogramaModel,
)
from src.infrastructure.persistence.models.perfil_contacto_model import PerfilContactoModel
from src.infrastructure.persistence.models.perfil_emocional_model import PerfilEmocionalModel
from src.infrastructure.persistence.models.perfil_tributario_model import PerfilTributarioModel
from src.shared.constants.cifrado import TABLA_PERFIL_CONTACTO
from src.shared.utils.cifrado_aad import construir_aad
from src.shared.utils.php_deserializer import (
    json_to_php_serialized,
    json_to_php_serialized_set,
    parse_php_serialized,
)


class SQLAlchemyPerfilRepo:
    def __init__(self, session: AsyncSession, cipher: CifradorCampos) -> None:
        self._session: AsyncSession = session
        self._cipher: CifradorCampos = cipher

    # ── Helpers de cifrado de campos restringidos (Medida C — AP-0147) ──────────

    def _desc(self, valor_enc: bytes | None, columna: str, doc: str) -> str | None:
        return self._cipher.descifrar(
            valor_enc, aad=construir_aad(TABLA_PERFIL_CONTACTO, columna, doc)
        )

    def _cif(self, valor: str | None, columna: str, doc: str) -> bytes | None:
        return self._cipher.cifrar(
            valor, aad=construir_aad(TABLA_PERFIL_CONTACTO, columna, doc)
        )

    # ── Perfil Contacto ────────────────────────────────────────────────────────

    def _contacto_to_entity(self, row: PerfilContactoModel) -> PerfilContactoEntity:
        doc: str = row.numero_documento
        return PerfilContactoEntity(
            numero_documento=row.numero_documento,
            tipo_documento=row.tipo_documento or "",
            nombre_completo=row.nombre_completo or "",
            genero=row.genero,
            fecha_nacimiento=row.fecha_nacimiento,
            telefono=self._desc(row.telefono_enc, "telefono", doc),
            celular=self._desc(row.celular_enc, "celular", doc),
            direccion=self._desc(row.direccion_enc, "direccion", doc),
            departamento=row.departamento,
            ciudad=row.ciudad,
            concesionario=row.concesionario,
            tipo_de_cuenta=self._desc(row.tipo_de_cuenta_enc, "tipo_de_cuenta", doc),
            banco=row.banco,
            numero_de_cuenta=self._desc(row.numero_de_cuenta_enc, "numero_de_cuenta", doc),
            acepto_habeas_data=row.acepto_habeas_data,
            estado=row.estado,
            fecha_completado=row.fecha_completado,
            cod_canales=row.cod_canales,
            cod_oficinas=row.cod_oficinas,
            comisionista_programa_id=row.comisionista_programa_id,
            comisionista_subprograma_id=row.comisionista_subprograma_id,
            requiere_comision=row.requiere_comision,
            incentivos=row.incentivos,
            usuario_responsable=row.usuario_responsable,
            segmentacion=row.segmentacion,
            firma_contrato=row.firma_contrato,
            motivo_inactivacion=row.motivo_inactivacion,
            programa_motivacion=row.programa_motivacion,
            email=self._desc(row.email_enc, "email", doc),
            email_verificado=row.email_verificado,
            email_verificado_fecha=row.email_verificado_fecha,
        )

    async def obtener_contacto_async(self, numero_documento: str) -> PerfilContactoEntity | None:
        result = await self._session.execute(
            select(PerfilContactoModel).where(
                PerfilContactoModel.numero_documento == numero_documento
            )
        )
        row: PerfilContactoModel | None = result.scalar_one_or_none()
        return self._contacto_to_entity(row) if row else None

    async def guardar_contacto_async(self, entity: PerfilContactoEntity) -> PerfilContactoEntity:
        result = await self._session.execute(
            select(PerfilContactoModel).where(
                PerfilContactoModel.numero_documento == entity.numero_documento
            )
        )
        row: PerfilContactoModel | None = result.scalar_one_or_none()
        if row is None:
            row = PerfilContactoModel()
            self._session.add(row)
        doc: str = entity.numero_documento
        row.numero_documento = entity.numero_documento
        row.tipo_documento = entity.tipo_documento
        row.nombre_completo = entity.nombre_completo
        row.genero = entity.genero
        row.fecha_nacimiento = entity.fecha_nacimiento
        row.telefono_enc = self._cif(entity.telefono, "telefono", doc)
        row.celular_enc = self._cif(entity.celular, "celular", doc)
        row.direccion_enc = self._cif(entity.direccion, "direccion", doc)
        row.departamento = entity.departamento
        row.ciudad = entity.ciudad
        row.concesionario = entity.concesionario
        row.tipo_de_cuenta_enc = self._cif(entity.tipo_de_cuenta, "tipo_de_cuenta", doc)
        row.banco = entity.banco
        row.numero_de_cuenta_enc = self._cif(entity.numero_de_cuenta, "numero_de_cuenta", doc)
        row.acepto_habeas_data = entity.acepto_habeas_data
        row.estado = entity.estado
        row.fecha_completado = entity.fecha_completado
        row.cod_canales = entity.cod_canales
        row.cod_oficinas = entity.cod_oficinas
        row.comisionista_programa_id = entity.comisionista_programa_id
        row.comisionista_subprograma_id = entity.comisionista_subprograma_id
        row.requiere_comision = entity.requiere_comision
        row.incentivos = entity.incentivos
        row.usuario_responsable = entity.usuario_responsable
        row.segmentacion = entity.segmentacion
        row.firma_contrato = entity.firma_contrato
        row.motivo_inactivacion = entity.motivo_inactivacion
        row.programa_motivacion = entity.programa_motivacion
        # Si el correo cambia respecto al almacenado, la verificación previa deja de
        # ser válida (el nuevo correo no se ha probado) → se resetea (AP-0004).
        email_anterior: str | None = self._desc(row.email_enc, "email", doc) if row.email_enc else None
        if email_anterior != entity.email:
            row.email_verificado = False
            row.email_verificado_fecha = None
        row.email_enc = self._cif(entity.email, "email", doc)
        await self._session.flush()
        return entity

    async def marcar_email_verificado_async(
        self, numero_documento: str, fecha: datetime
    ) -> None:
        result = await self._session.execute(
            select(PerfilContactoModel).where(
                PerfilContactoModel.numero_documento == numero_documento
            )
        )
        row: PerfilContactoModel | None = result.scalar_one_or_none()
        if row is None:
            raise LookupError("Perfil de contacto no encontrado")
        row.email_verificado = True
        row.email_verificado_fecha = fecha
        await self._session.flush()

    async def numero_documento_por_email_async(self, email: str) -> str | None:
        """AP-0141: documento del perfil cuyo correo coincide, o None.

        El correo se guarda cifrado con nonce aleatorio (no se puede comparar
        por ciphertext), asi que se descifra y compara normalizado. Sirve para
        garantizar unicidad del correo en el registro.
        """
        objetivo: str = email.strip().lower()
        if not objetivo:
            return None
        result = await self._session.execute(
            select(
                PerfilContactoModel.numero_documento, PerfilContactoModel.email_enc
            ).where(PerfilContactoModel.email_enc.is_not(None))
        )
        for doc, email_enc in result.all():
            descifrado: str | None = self._desc(email_enc, "email", doc)
            if descifrado is not None and descifrado.strip().lower() == objetivo:
                return doc
        return None

    # ── Perfil Tributario ──────────────────────────────────────────────────────

    @staticmethod
    def _tributario_to_entity(row: PerfilTributarioModel) -> PerfilTributarioEntity:
        return PerfilTributarioEntity(
            numero_documento=row.numero_documento,
            salarios_y_prestaciones=float(row.salarios_y_prestaciones) if row.salarios_y_prestaciones is not None else None,
            comisiones=float(row.comisiones) if row.comisiones is not None else None,
            honorarios=float(row.honorarios) if row.honorarios is not None else None,
            servicio_no=float(row.servicio_no) if row.servicio_no is not None else None,
            servicio=float(row.servicio) if row.servicio is not None else None,
            dividendos=float(row.dividendos) if row.dividendos is not None else None,
            arrendamientos=float(row.arrendamientos) if row.arrendamientos is not None else None,
            rendimientos_financieros=float(row.rendimientos_financieros) if row.rendimientos_financieros is not None else None,
            ingresos_por_pension=float(row.ingresos_por_pension) if row.ingresos_por_pension is not None else None,
            actividades_deportivas=float(row.actividades_deportivas) if row.actividades_deportivas is not None else None,
            agropecuario=float(row.agropecuario) if row.agropecuario is not None else None,
            comercio_mayor=float(row.comercio_mayor) if row.comercio_mayor is not None else None,
            comercio_menor=float(row.comercio_menor) if row.comercio_menor is not None else None,
            comercio_vehiculos=float(row.comercio_vehiculos) if row.comercio_vehiculos is not None else None,
            construccion=float(row.construccion) if row.construccion is not None else None,
            electricidad_gas=float(row.electricidad_gas) if row.electricidad_gas is not None else None,
            fabricacion_minerales=float(row.fabricacion_minerales) if row.fabricacion_minerales is not None else None,
            fabricacion_sustancias=float(row.fabricacion_sustancias) if row.fabricacion_sustancias is not None else None,
            industria_madera=float(row.industria_madera) if row.industria_madera is not None else None,
            manufactura_alimentos=float(row.manufactura_alimentos) if row.manufactura_alimentos is not None else None,
            manufactura_textiles=float(row.manufactura_textiles) if row.manufactura_textiles is not None else None,
            mineria=float(row.mineria) if row.mineria is not None else None,
            servicios_transporte=float(row.servicios_transporte) if row.servicios_transporte is not None else None,
            servicios_de_hoteles=float(row.servicios_de_hoteles) if row.servicios_de_hoteles is not None else None,
            servicios_financieros=float(row.servicios_financieros) if row.servicios_financieros is not None else None,
            otro=float(row.otro) if row.otro is not None else None,
            otros_cual=row.otros_cual,
            declaracion_renta=row.declaracion_renta,
            ingresos_mayor=row.ingresos_mayor,
            eps=row.eps,
            afp=row.afp,
            arl=row.arl,
            total=float(row.total) if row.total is not None else None,
            estado=row.estado,
            fecha_alta=row.fecha_alta,
            renta_financiero=float(row.renta_financiero) if row.renta_financiero is not None else None,
            renta_dividendos=float(row.renta_dividendos) if row.renta_dividendos is not None else None,
            fondo_pensiones=row.fondo_pensiones,
            nombre_eps=row.nombre_eps,
            nombre_afp=row.nombre_afp,
            nombre_arl=row.nombre_arl,
            deleted=row.deleted,
            contratacion_personal=row.contratacion_personal,
            regimen_iva=row.regimen_iva,
        )

    async def obtener_tributario_async(self, numero_documento: str) -> PerfilTributarioEntity | None:
        result = await self._session.execute(
            select(PerfilTributarioModel).where(
                PerfilTributarioModel.numero_documento == numero_documento
            )
        )
        row: PerfilTributarioModel | None = result.scalar_one_or_none()
        return self._tributario_to_entity(row) if row else None

    async def guardar_tributario_async(self, entity: PerfilTributarioEntity) -> PerfilTributarioEntity:
        result = await self._session.execute(
            select(PerfilTributarioModel).where(
                PerfilTributarioModel.numero_documento == entity.numero_documento
            )
        )
        row: PerfilTributarioModel | None = result.scalar_one_or_none()
        if row is None:
            row = PerfilTributarioModel()
            self._session.add(row)
        row.numero_documento = entity.numero_documento
        row.salarios_y_prestaciones = entity.salarios_y_prestaciones
        row.comisiones = entity.comisiones
        row.honorarios = entity.honorarios
        row.servicio_no = entity.servicio_no
        row.servicio = entity.servicio
        row.dividendos = entity.dividendos
        row.arrendamientos = entity.arrendamientos
        row.rendimientos_financieros = entity.rendimientos_financieros
        row.ingresos_por_pension = entity.ingresos_por_pension
        row.actividades_deportivas = entity.actividades_deportivas
        row.agropecuario = entity.agropecuario
        row.comercio_mayor = entity.comercio_mayor
        row.comercio_menor = entity.comercio_menor
        row.comercio_vehiculos = entity.comercio_vehiculos
        row.construccion = entity.construccion
        row.electricidad_gas = entity.electricidad_gas
        row.fabricacion_minerales = entity.fabricacion_minerales
        row.fabricacion_sustancias = entity.fabricacion_sustancias
        row.industria_madera = entity.industria_madera
        row.manufactura_alimentos = entity.manufactura_alimentos
        row.manufactura_textiles = entity.manufactura_textiles
        row.mineria = entity.mineria
        row.servicios_transporte = entity.servicios_transporte
        row.servicios_de_hoteles = entity.servicios_de_hoteles
        row.servicios_financieros = entity.servicios_financieros
        row.otro = entity.otro
        row.otros_cual = entity.otros_cual
        row.declaracion_renta = entity.declaracion_renta
        row.ingresos_mayor = entity.ingresos_mayor
        row.eps = entity.eps
        row.afp = entity.afp
        row.arl = entity.arl
        row.total = entity.total
        row.estado = entity.estado
        row.fecha_alta = entity.fecha_alta
        row.renta_financiero = entity.renta_financiero
        row.renta_dividendos = entity.renta_dividendos
        row.fondo_pensiones = entity.fondo_pensiones
        row.nombre_eps = entity.nombre_eps
        row.nombre_afp = entity.nombre_afp
        row.nombre_arl = entity.nombre_arl
        row.deleted = entity.deleted
        row.contratacion_personal = entity.contratacion_personal
        row.regimen_iva = entity.regimen_iva
        await self._session.flush()
        return entity

    # ── Perfil Emocional ───────────────────────────────────────────────────────

    @staticmethod
    def _emocional_to_entity(row: PerfilEmocionalModel) -> PerfilEmocionalEntity:
        return PerfilEmocionalEntity(
            numero_documento=row.numero_documento,
            con_quien_vives=parse_php_serialized(row.con_quien_vives),
            estado_civil=row.estado_civil,
            numero_hijos=row.numero_hijos,
            info_hijos=parse_php_serialized(row.info_hijos),
            hobbies=parse_php_serialized(row.hobbies),
            premios_gustaria_recibir=parse_php_serialized(row.premios_gustaria_recibir),
            nivel_educativo=row.nivel_educativo,
            profesion=row.profesion,
            numero_mascotas=row.numero_mascotas,
            info_mascotas=parse_php_serialized(row.info_mascotas),
            temas_a_profundizar=parse_php_serialized(row.temas_a_profundizar),
            acepto_terminos_y_condiciones=row.acepto_terminos_y_condiciones,
            comisionista_programa_id=row.comisionista_programa_id,
            info_premios=row.info_premios,
            propositos_familiares=parse_php_serialized(row.propositos_familiares),
            propositos_financieros=parse_php_serialized(row.propositos_financieros),
            propositos_diversion=parse_php_serialized(row.propositos_diversion),
            propositos_salud=parse_php_serialized(row.propositos_salud),
            propositos_competencias=parse_php_serialized(row.propositos_competencias),
        )

    async def obtener_emocional_async(self, numero_documento: str) -> PerfilEmocionalEntity | None:
        result = await self._session.execute(
            select(PerfilEmocionalModel).where(
                PerfilEmocionalModel.numero_documento == numero_documento
            )
        )
        row: PerfilEmocionalModel | None = result.scalar_one_or_none()
        return self._emocional_to_entity(row) if row else None

    async def guardar_emocional_async(self, entity: PerfilEmocionalEntity) -> PerfilEmocionalEntity:
        result = await self._session.execute(
            select(PerfilEmocionalModel).where(
                PerfilEmocionalModel.numero_documento == entity.numero_documento
            )
        )
        row: PerfilEmocionalModel | None = result.scalar_one_or_none()
        if row is None:
            row = PerfilEmocionalModel()
            self._session.add(row)
        row.numero_documento = entity.numero_documento
        row.con_quien_vives = json_to_php_serialized_set(entity.con_quien_vives)
        row.estado_civil = entity.estado_civil
        row.numero_hijos = entity.numero_hijos
        row.info_hijos = json_to_php_serialized(entity.info_hijos)
        row.hobbies = json_to_php_serialized_set(entity.hobbies)
        row.premios_gustaria_recibir = json_to_php_serialized_set(entity.premios_gustaria_recibir)
        row.nivel_educativo = entity.nivel_educativo
        row.profesion = entity.profesion
        row.numero_mascotas = entity.numero_mascotas
        row.info_mascotas = json_to_php_serialized(entity.info_mascotas)
        row.temas_a_profundizar = json_to_php_serialized_set(entity.temas_a_profundizar)
        row.acepto_terminos_y_condiciones = entity.acepto_terminos_y_condiciones
        row.comisionista_programa_id = entity.comisionista_programa_id
        row.info_premios = entity.info_premios
        row.propositos_familiares = json_to_php_serialized_set(entity.propositos_familiares)
        row.propositos_financieros = json_to_php_serialized_set(entity.propositos_financieros)
        row.propositos_diversion = json_to_php_serialized_set(entity.propositos_diversion)
        row.propositos_salud = json_to_php_serialized_set(entity.propositos_salud)
        row.propositos_competencias = json_to_php_serialized_set(entity.propositos_competencias)
        await self._session.flush()
        return entity

    # ── Catálogos ─────────────────────────────────────────────────────────────

    async def listar_programas_async(self) -> list[ComisionistaProgramaEntity]:
        result = await self._session.execute(select(ComisionistaProgramaModel))
        return [ComisionistaProgramaEntity(cpid=row.cpid, cp_nombre=row.cp_nombre) for row in result.scalars().all()]

    async def listar_subprogramas_async(self, cpid: int | None = None) -> list[ComisionistaSubprogramaEntity]:
        stmt = select(ComisionistaSubprogramaModel)
        if cpid is not None:
            stmt = stmt.where(ComisionistaSubprogramaModel.cpid == cpid)
        result = await self._session.execute(stmt)
        return [
            ComisionistaSubprogramaEntity(cspid=row.cspid, cspid_nombre=row.cspid_nombre or "", cpid=row.cpid)
            for row in result.scalars().all()
        ]
