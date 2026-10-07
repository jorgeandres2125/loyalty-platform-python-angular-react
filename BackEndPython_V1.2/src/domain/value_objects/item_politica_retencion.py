from __future__ import annotations

from dataclasses import dataclass

from src.domain.value_objects.retencion_categoria import RetencionCategoria


@dataclass(frozen=True, slots=True)
class ItemPoliticaRetencion:
    """AP-0026: una entrada de la politica de retencion (categoria, dias, base regulatoria)."""

    categoria: RetencionCategoria
    dias: int
    base_regulatoria: str
