from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.ejecutivo.ejecutivo_list_item import EjecutivoListItem


class EjecutivoListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[EjecutivoListItem]
    total: int
    page: int
    page_size: int
