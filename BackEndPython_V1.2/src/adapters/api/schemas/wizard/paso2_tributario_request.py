from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Paso2TributarioRequest(BaseModel):
    """Paso 2 — Datos tributarios (solo programa Movilidad)."""

    model_config = ConfigDict(extra="forbid")

    numero_documento: str = Field(min_length=3, max_length=50)
    eps: int | None = None
    nombre_eps: str | None = Field(default=None, max_length=100)
    afp: int | None = None
    nombre_afp: str | None = Field(default=None, max_length=100)
    fondo_pensiones: str | None = Field(default=None, max_length=50)
    arl: int | None = None
    nombre_arl: str | None = Field(default=None, max_length=100)
    declaracion_renta: int | None = None
    ingresos_mayor: int | None = None
    contratacion_personal: int | None = None
    regimen_iva: int | None = None
    salarios_y_prestaciones: float | None = None
    comisiones: float | None = None
    honorarios: float | None = None
    servicio_no: float | None = None
    servicio: float | None = None
    dividendos: float | None = None
    arrendamientos: float | None = None
    rendimientos_financieros: float | None = None
    ingresos_por_pension: float | None = None
    actividades_deportivas: float | None = None
    agropecuario: float | None = None
    comercio_mayor: float | None = None
    comercio_menor: float | None = None
    comercio_vehiculos: float | None = None
    construccion: float | None = None
    electricidad_gas: float | None = None
    fabricacion_minerales: float | None = None
    fabricacion_sustancias: float | None = None
    industria_madera: float | None = None
    manufactura_alimentos: float | None = None
    manufactura_textiles: float | None = None
    mineria: float | None = None
    servicios_transporte: float | None = None
    servicios_de_hoteles: float | None = None
    servicios_financieros: float | None = None
    renta_financiero: float | None = None
    renta_dividendos: float | None = None
    otro: float | None = None
    otros_cual: str | None = Field(default=None, max_length=250)
    total: float | None = None
