from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoVerificacionDTO:
    """Resultado de confirmar un código de verificación de correo (AP-0004)."""

    verificado: bool
    numero_documento: str
