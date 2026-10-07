from __future__ import annotations

from pydantic import BaseModel

from src.adapters.api.schemas.retencion.item_politica_retencion_response import (
    ItemPoliticaRetencionResponse,
)


class PoliticaRetencionResponse(BaseModel):
    """AP-0026: politica de retencion de logs vigente (evidencia de cumplimiento)."""

    items: list[ItemPoliticaRetencionResponse]
    total: int
