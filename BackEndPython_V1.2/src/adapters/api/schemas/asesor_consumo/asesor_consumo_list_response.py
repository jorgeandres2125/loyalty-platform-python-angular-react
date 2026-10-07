from __future__ import annotations

from pydantic import BaseModel

from src.adapters.api.schemas.asesor_consumo.asesor_consumo_item import AsesorConsumoItem


class AsesorConsumoListResponse(BaseModel):
    items: list[AsesorConsumoItem]
    total: int
    page: int
    size: int
    pages: int
