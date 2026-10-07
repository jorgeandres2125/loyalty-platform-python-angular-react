from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from .perfil_contacto_model import PerfilContactoModel


class PerfilTributarioModel(Base):
    __tablename__ = "users_perfil_tributario"

    # PK = FK 1:1 al perfil de contacto. Unificada a nvarchar(40) (ADR-02).
    numero_documento: Mapped[str] = mapped_column(
        String(40),
        ForeignKey("users_perfil_contacto.numero_documento", ondelete="CASCADE"),
        primary_key=True,
    )
    salarios_y_prestaciones: Mapped[float | None] = mapped_column(Numeric(10, 1))
    comisiones: Mapped[float | None] = mapped_column(Numeric(10, 1))
    honorarios: Mapped[float | None] = mapped_column(Numeric(10, 1))
    servicio_no: Mapped[float | None] = mapped_column(Numeric(10, 1))
    servicio: Mapped[float | None] = mapped_column(Numeric(10, 1))
    dividendos: Mapped[float | None] = mapped_column(Numeric(10, 1))
    arrendamientos: Mapped[float | None] = mapped_column(Numeric(10, 1))
    rendimientos_financieros: Mapped[float | None] = mapped_column(Numeric(10, 1))
    ingresos_por_pension: Mapped[float | None] = mapped_column(Numeric(10, 1))
    actividades_deportivas: Mapped[float | None] = mapped_column(Numeric(10, 1))
    agropecuario: Mapped[float | None] = mapped_column(Numeric(10, 1))
    comercio_mayor: Mapped[float | None] = mapped_column(Numeric(10, 1))
    comercio_menor: Mapped[float | None] = mapped_column(Numeric(10, 1))
    comercio_vehiculos: Mapped[float | None] = mapped_column(Numeric(10, 1))
    construccion: Mapped[float | None] = mapped_column(Numeric(10, 1))
    electricidad_gas: Mapped[float | None] = mapped_column(Numeric(10, 1))
    fabricacion_minerales: Mapped[float | None] = mapped_column(Numeric(10, 1))
    fabricacion_sustancias: Mapped[float | None] = mapped_column(Numeric(10, 1))
    industria_madera: Mapped[float | None] = mapped_column(Numeric(10, 1))
    manufactura_alimentos: Mapped[float | None] = mapped_column(Numeric(10, 1))
    manufactura_textiles: Mapped[float | None] = mapped_column(Numeric(10, 1))
    mineria: Mapped[float | None] = mapped_column(Numeric(10, 1))
    servicios_transporte: Mapped[float | None] = mapped_column(Numeric(10, 1))
    servicios_de_hoteles: Mapped[float | None] = mapped_column(Numeric(10, 1))
    servicios_financieros: Mapped[float | None] = mapped_column(Numeric(10, 1))
    otro: Mapped[float | None] = mapped_column(Numeric(10, 1))
    otros_cual: Mapped[str | None] = mapped_column(String(250))
    declaracion_renta: Mapped[int | None] = mapped_column(Integer)
    ingresos_mayor: Mapped[int | None] = mapped_column(Integer)
    # Catálogos opcionales: al borrar el catálogo, el perfil sobrevive (SET NULL).
    # Columnas nullable (obligatorio para SET NULL).
    eps: Mapped[int | None] = mapped_column(ForeignKey("eps.tid", ondelete="SET NULL"))
    afp: Mapped[int | None] = mapped_column(ForeignKey("afp.tid", ondelete="SET NULL"))
    arl: Mapped[int | None] = mapped_column(ForeignKey("arl.tid", ondelete="SET NULL"))
    total: Mapped[float | None] = mapped_column(Numeric(15, 1))
    estado: Mapped[int | None] = mapped_column(Integer)
    fecha_alta: Mapped[date | None] = mapped_column(Date)
    renta_financiero: Mapped[float | None] = mapped_column(Numeric(10, 1))
    renta_dividendos: Mapped[float | None] = mapped_column(Numeric(10, 1))
    fondo_pensiones: Mapped[str | None] = mapped_column(String(50))
    nombre_eps: Mapped[str | None] = mapped_column(String(100))
    nombre_afp: Mapped[str | None] = mapped_column(String(100))
    nombre_arl: Mapped[str | None] = mapped_column(String(100))
    deleted: Mapped[int | None] = mapped_column(Integer)
    contratacion_personal: Mapped[int | None] = mapped_column(SmallInteger)
    regimen_iva: Mapped[int | None] = mapped_column(SmallInteger)

    contacto: Mapped[PerfilContactoModel] = relationship(
        "PerfilContactoModel", lazy="select"
    )
