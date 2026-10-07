from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class VerificarFirmaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valida: bool
    kid: str
    alg: str
    mensaje: str
