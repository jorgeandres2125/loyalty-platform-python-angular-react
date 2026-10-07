from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PasswordTemporalRequest(BaseModel):
    """AP-0047: emision de contrasena temporal por un tercero autorizado.

    El origen distingue el rol funcional del emisor (admin del portal u operador
    de soporte); SISTEMA queda reservado a la provision automatica y no es
    seleccionable desde la API.
    """

    model_config = ConfigDict(extra="forbid")

    origen: Literal["admin", "soporte"] = "admin"
    motivo: str | None = Field(default=None, max_length=200)
