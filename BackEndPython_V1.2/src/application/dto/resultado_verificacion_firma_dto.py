from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoVerificacionFirmaDTO:
    """AP-0006: resultado de verificar una firma digital."""

    valida: bool
    kid: str
    alg: str
