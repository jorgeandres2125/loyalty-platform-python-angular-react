from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class PerfilContactoEntity:
    numero_documento: str
    tipo_documento: str = ""
    nombre_completo: str = ""
    genero: str | None = None
    fecha_nacimiento: date | None = None
    telefono: str | None = None
    celular: str | None = None
    direccion: str | None = None
    departamento: str | None = None
    ciudad: str | None = None
    concesionario: str | None = None
    tipo_de_cuenta: str | None = None
    banco: int | None = None
    numero_de_cuenta: str | None = None
    acepto_habeas_data: int | None = None
    estado: int | None = None
    fecha_completado: date | None = None
    cod_canales: int | None = None
    cod_oficinas: int | None = None
    comisionista_programa_id: int | None = None
    comisionista_subprograma_id: int | None = None
    requiere_comision: bool | None = None
    incentivos: bool | None = None
    usuario_responsable: int | None = None
    segmentacion: str | None = None
    firma_contrato: bool | None = None
    motivo_inactivacion: int | None = None
    programa_motivacion: str | None = None
    email: str | None = None
    # Verificación de propiedad del correo (AP-0004 — doble opt-in).
    email_verificado: bool | None = None
    email_verificado_fecha: datetime | None = None
    # Enriched join fields — populated only by queries with JOINs, not stored in DB
    nom_canales: str | None = None
    nom_oficinas: str | None = None
    id_oficinas: int | None = None
    cp_nombre: str | None = None
    cspid_nombre: str | None = None
    dep_did: int | None = None
    dep_pid: int | None = None
    dep_nombre: str | None = None
    ciu_cid: int | None = None
    ciu_did: int | None = None
    ciu_nombre: str | None = None
