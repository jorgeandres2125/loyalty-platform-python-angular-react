from __future__ import annotations

from dataclasses import dataclass

from src.domain.value_objects.retencion_categoria import RetencionCategoria


@dataclass(frozen=True, slots=True)
class ResultadoRetencion:
    """AP-0026: categoria y plazo (en dias) de retencion resueltos para un evento."""

    categoria: RetencionCategoria
    dias: int
