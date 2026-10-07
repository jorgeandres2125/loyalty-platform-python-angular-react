from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class VerificarOtpRequest(BaseModel):
    """AP-0012: paso 2 del login â€” el usuario ingresa el codigo OTP recibido."""

    model_config = ConfigDict(extra="forbid")

    desafio_id: str = Field(min_length=1, max_length=64)
    codigo: str = Field(pattern=r"^\d{6}$", description="6 digitos exactos")
    fingerprint: str | None = Field(
        default=None, max_length=256, description="Huella del dispositivo (AP-0014)"
    )
    device_name: str | None = Field(
        default=None, max_length=200, description="Nombre del dispositivo (AP-0014)"
    )
