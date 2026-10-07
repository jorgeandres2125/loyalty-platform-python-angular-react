from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Paso3EmocionalRequest(BaseModel):
    """Paso 3 — Perfil emocional (compartido Consumo y Movilidad)."""

    model_config = ConfigDict(extra="forbid")

    numero_documento: str = Field(min_length=3, max_length=50)
    con_quien_vives: str | None = Field(default=None, max_length=400)
    estado_civil: str | None = Field(default=None, max_length=220)
    numero_hijos: str | None = Field(default=None, max_length=220)
    info_hijos: str | None = Field(default=None, max_length=2000)
    hobbies: str | None = Field(default=None, max_length=2000)
    premios_gustaria_recibir: str | None = Field(default=None, max_length=220)
    nivel_educativo: str | None = Field(default=None, max_length=220)
    profesion: str | None = Field(default=None, max_length=220)
    numero_mascotas: str | None = Field(default=None, max_length=220)
    info_mascotas: str | None = Field(default=None, max_length=2000)
    temas_a_profundizar: str | None = Field(default=None, max_length=240)
    comisionista_programa_id: int | None = None
    info_premios: str | None = Field(default=None, max_length=300)
    propositos_familiares: str | None = Field(default=None, max_length=2000)
    propositos_financieros: str | None = Field(default=None, max_length=2000)
    propositos_diversion: str | None = Field(default=None, max_length=2000)
    propositos_salud: str | None = Field(default=None, max_length=2000)
    propositos_competencias: str | None = Field(default=None, max_length=2000)
    acepto_terminos_y_condiciones: Literal[1] = Field(description="Debe ser 1 para aceptar los términos")
