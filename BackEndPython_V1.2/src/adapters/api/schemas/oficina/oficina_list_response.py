from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.oficina.oficina_list_item import OficinaListItem


class OficinaListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[OficinaListItem]
    total: int
    page: int
    page_size: int
