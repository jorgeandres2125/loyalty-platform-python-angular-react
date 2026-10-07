from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.admin.eps.eps_list_item import EpsListItem


class EpsListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[EpsListItem]
    total: int
    page: int
    page_size: int
