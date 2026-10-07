from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConfirmarCodigoRequest(BaseModel):
    """Paso 2 — el usuario ingresa el código de 8 dígitos recibido por correo."""

    model_config = ConfigDict(extra="forbid")

    tipo_documento: str = Field(default="C.C.", max_length=5)
    numero_documento: str = Field(min_length=3, max_length=20)
    codigo: str = Field(pattern=r"^\d{8}$", description="8 dígitos exactos")

    @field_validator("numero_documento")
    @classmethod
    def validar_solo_digitos(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("El número de documento debe contener solo dígitos")
        return v
