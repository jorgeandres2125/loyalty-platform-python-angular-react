from __future__ import annotations

from pydantic import BaseModel

from src.adapters.api.schemas.asesor_movilidad.asesor_movilidad_item import (
    AsesorMovilidadItem,
)


class AsesorMovilidadListResponse(BaseModel):
    items: list[AsesorMovilidadItem]
    total: int
    page: int
    size: int
    pages: int
