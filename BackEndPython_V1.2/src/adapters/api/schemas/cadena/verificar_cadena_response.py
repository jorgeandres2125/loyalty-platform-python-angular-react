from __future__ import annotations

from pydantic import BaseModel


class VerificarCadenaResponse(BaseModel):
    """AP-0025: resultado de la verificacion de integridad de la cadena."""

    integra: bool
    total: int
    primer_roto: int | None
    motivo: str
    mensaje: str
