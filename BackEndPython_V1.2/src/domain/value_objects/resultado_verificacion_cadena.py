from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResultadoVerificacionCadena:
    """AP-0025: resultado de verificar la integridad de una cadena de sellos.

    `integra` es verdadero cuando la cadena completa es consistente. Si se rompe,
    `primer_roto` indica el numero de secuencia del primer eslabon inconsistente y
    `motivo` describe la causa (secuencia no consecutiva, enlace roto o hash recalculado
    que no coincide).
    """

    integra: bool
    total: int
    primer_roto: int | None
    motivo: str
