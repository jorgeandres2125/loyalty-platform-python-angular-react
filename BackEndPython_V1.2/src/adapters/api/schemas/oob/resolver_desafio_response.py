from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ResolverDesafioResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: str
    aprobado: bool
    tipo_transaccion: str | None = None
    payload_hash: str | None = None
    mensaje: str
