from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Paso1ContactoRequest(BaseModel):
    """Paso 1 — Datos de contacto (compartido Consumo y Movilidad)."""

    model_config = ConfigDict(extra="forbid")

    numero_documento: str = Field(min_length=3, max_length=20)
    tipo_documento: str = Field(default="C.C.", max_length=5)
    nombre_completo: str = Field(min_length=3, max_length=100)
    genero: str = Field(max_length=10)
    fecha_nacimiento: date
    celular: str = Field(pattern=r"^\d{10}$", description="10 dígitos exactos")
    telefono: str | None = Field(default=None, max_length=18)
    email: str | None = Field(default=None, max_length=254)
    direccion: str = Field(min_length=8, max_length=250)
    departamento: str = Field(min_length=1, max_length=40)
    ciudad: str = Field(min_length=1, max_length=40)
    comisionista_programa_id: int = Field(ge=1)
    comisionista_subprograma_id: int | None = Field(default=None, ge=1)
    cod_canales: int | None = None
    cod_oficinas: int | None = None
    usuario_responsable: int | None = None
    concesionario: str | None = Field(default=None, max_length=30)
    tipo_de_cuenta: str | None = Field(default=None, max_length=20)
    banco: int | None = None
    numero_de_cuenta: str | None = Field(default=None, max_length=30)
    requiere_comision: bool | None = None
    acepto_habeas_data: Literal[1] = Field(description="Debe ser 1 para aceptar habeas data")
    incentivos: bool = Field(description="True si el asesor tiene incentivos")
    estado: Literal[0, 1] = Field(description="1=Activo, 0=Inactivo")
    firma_contrato: bool | None = None

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_edad_minima(cls, v: date) -> date:
        from datetime import date as dt
        hoy: dt = dt.today()
        edad: int = hoy.year - v.year - ((hoy.month, hoy.day) < (v.month, v.day))
        if edad < 18:
            raise ValueError("El comisionista debe tener al menos 18 años")
        return v

    @field_validator("numero_documento")
    @classmethod
    def validar_solo_digitos(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("El número de documento debe contener solo dígitos")
        return v

    @field_validator("email")
    @classmethod
    def validar_email_rfc822(cls, valor: str | None) -> str | None:
        if not valor:
            return valor
        from src.domain.value_objects.email import Email

        return Email(valor).valor
