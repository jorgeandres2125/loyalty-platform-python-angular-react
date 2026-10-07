from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SolicitarCodigoRequest(BaseModel):
    """Paso 1 — el usuario pide que se le envíe el código a su correo declarado."""

    model_config = ConfigDict(extra="forbid")

    tipo_documento: str = Field(default="C.C.", max_length=5)
    numero_documento: str = Field(min_length=3, max_length=20)

    @field_validator("numero_documento")
    @classmethod
    def validar_solo_digitos(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("El número de documento debe contener solo dígitos")
        return v
