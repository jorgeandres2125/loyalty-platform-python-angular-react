from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoFirmaDTO:
    """AP-0006: resultado de firmar un recurso sensible."""

    evidencia_id: str
    kid: str
    alg: str
    valor_firma: str
    hash_payload: str
    hash_evidencia: str
