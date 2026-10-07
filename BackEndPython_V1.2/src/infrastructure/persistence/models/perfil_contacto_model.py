from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    SmallInteger,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from .banco_model import BancoModel
    from .canal_model import CanalModel
    from .comisionista_programa_model import ComisionistaProgramaModel
    from .comisionista_subprograma_model import ComisionistaSubprogramaModel
    from .oficina_model import OficinaModel


class PerfilContactoModel(Base):
    __tablename__ = "users_perfil_contacto"

    # PK unificada a nvarchar(40) (ADR-02) — antes nvarchar(20). Es padre de los
    # perfiles tributario/emocional y de user_documento, por lo que todos deben
    # compartir el mismo tipo para que los FK 1:1 / 1:N sean válidos.
    numero_documento: Mapped[str] = mapped_column(String(40), primary_key=True)
    tipo_documento: Mapped[str | None] = mapped_column(String(5))
    nombre_completo: Mapped[str | None] = mapped_column(String(100))
    genero: Mapped[str | None] = mapped_column(String(10))
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date)
    # PII de contacto restringido cifrado a nivel de aplicación (Medida C — AP-0147).
    telefono_enc: Mapped[bytes | None] = mapped_column(LargeBinary)
    celular_enc: Mapped[bytes | None] = mapped_column(LargeBinary)
    direccion_enc: Mapped[bytes | None] = mapped_column(LargeBinary)
    # ciudad/departamento guardan códigos DANE como texto (ej. '76001'/'76'),
    # no IDs int de ciudades/departamentos → se preservan como texto (sin FK).
    departamento: Mapped[str | None] = mapped_column(String(40))
    ciudad: Mapped[str | None] = mapped_column(String(40))
    concesionario: Mapped[str | None] = mapped_column(String(30))
    # Campos restringidos cifrados a nivel de aplicación (Medida C — AP-0147/AP-0095).
    # Persistidos como VARBINARY(MAX) con AES-256-GCM; el valor en claro vive solo en
    # la entidad de dominio. Cifrado/descifrado en SQLAlchemyPerfilRepo (AesGcmFieldCipher).
    tipo_de_cuenta_enc: Mapped[bytes | None] = mapped_column(LargeBinary)
    # Catálogo opcional: al borrar el banco, el perfil sobrevive (SET NULL).
    banco: Mapped[int | None] = mapped_column(
        ForeignKey("bancos.tid", ondelete="SET NULL"), index=True
    )
    numero_de_cuenta_enc: Mapped[bytes | None] = mapped_column(LargeBinary)
    acepto_habeas_data: Mapped[int | None] = mapped_column(Integer)
    estado: Mapped[int | None] = mapped_column(Integer)
    fecha_completado: Mapped[date | None] = mapped_column(Date)
    # Red comercial: al borrar canal/oficina el perfil sobrevive (SET NULL).
    cod_canales: Mapped[int | None] = mapped_column(
        ForeignKey("canales.cod_canales", ondelete="SET NULL"), index=True
    )
    cod_oficinas: Mapped[int | None] = mapped_column(
        ForeignKey("oficinas.cod_oficinas", ondelete="SET NULL"), index=True
    )
    # NO ACTION (sin ondelete) a propósito: evita el segundo camino de borrado
    # programa→contacto (el otro es programa→subprograma→contacto) que dispararía
    # el error 1785 de SQL Server (multiple cascade paths). El catálogo de
    # programas es dato de referencia y no se borra en operación normal.
    comisionista_programa_id: Mapped[int | None] = mapped_column(
        SmallInteger,
        ForeignKey("comisionistas_programa.cpid"),
        index=True,
    )
    # Ensanchado tinyint → int para casar con comisionistas_subprograma.cspid (int).
    comisionista_subprograma_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("comisionistas_subprograma.cspid", ondelete="SET NULL"),
        index=True,
    )
    requiere_comision: Mapped[bool | None] = mapped_column(Boolean)
    incentivos: Mapped[bool | None] = mapped_column(Boolean, default=False)
    # Responsable = uid del usuario Drupal que gestionó el registro.
    usuario_responsable: Mapped[int | None] = mapped_column(
        ForeignKey("users.uid", ondelete="SET NULL"), index=True
    )
    segmentacion: Mapped[str | None] = mapped_column(String(30))
    firma_contrato: Mapped[bool | None] = mapped_column(Boolean)
    motivo_inactivacion: Mapped[int | None] = mapped_column(Integer)
    programa_motivacion: Mapped[str | None] = mapped_column(String(50))
    email_enc: Mapped[bytes | None] = mapped_column(LargeBinary)
    # Verificación de propiedad del correo (AP-0004 — doble opt-in).
    email_verificado: Mapped[bool | None] = mapped_column(Boolean, default=False)
    email_verificado_fecha: Mapped[datetime | None] = mapped_column(DateTime)

    # ── Relaciones ORM (unidireccionales; cada una con un único camino FK) ──────
    banco_ref: Mapped[BancoModel | None] = relationship("BancoModel", lazy="select")
    canal: Mapped[CanalModel | None] = relationship("CanalModel", lazy="select")
    oficina: Mapped[OficinaModel | None] = relationship("OficinaModel", lazy="select")
    programa: Mapped[ComisionistaProgramaModel | None] = relationship(
        "ComisionistaProgramaModel", lazy="select"
    )
    subprograma: Mapped[ComisionistaSubprogramaModel | None] = relationship(
        "ComisionistaSubprogramaModel", lazy="select"
    )
