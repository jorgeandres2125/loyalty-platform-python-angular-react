from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionAcceso:
    """AP-0055: resultado de una evaluacion de autorizacion a nivel de objeto."""

    permitido: bool
    status: int = 200
    mensaje: str = ""
    motivo: str = ""
