from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoResolverOobDTO:
    """AP-0005: resultado de resolver (aprobar o rechazar) un desafio OOB."""

    estado: str
    aprobado: bool
    tipo_transaccion: str | None = None
    payload_hash: str | None = None
