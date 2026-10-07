from dataclasses import dataclass
from datetime import date


@dataclass
class PerfilTributarioEntity:
    numero_documento: str
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
    otro: float | None = None
    otros_cual: str | None = None
    declaracion_renta: int | None = None
    ingresos_mayor: int | None = None
    eps: int | None = None
    afp: int | None = None
    arl: int | None = None
    total: float | None = None
    estado: int | None = None
    fecha_alta: date | None = None
    renta_financiero: float | None = None
    renta_dividendos: float | None = None
    fondo_pensiones: str | None = None
    nombre_eps: str | None = None
    nombre_afp: str | None = None
    nombre_arl: str | None = None
    deleted: int | None = None
    contratacion_personal: int | None = None
    regimen_iva: int | None = None
