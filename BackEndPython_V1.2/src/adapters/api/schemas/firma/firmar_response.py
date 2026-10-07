from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class FirmarResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidencia_id: str
    kid: str
    alg: str
    valor_firma: str
    hash_payload: str
    hash_evidencia: str
    mensaje: str
