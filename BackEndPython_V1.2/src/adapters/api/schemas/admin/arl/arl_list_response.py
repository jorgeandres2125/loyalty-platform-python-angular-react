from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.admin.arl.arl_list_item import ArlListItem


class ArlListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[ArlListItem]
    total: int
    page: int
    page_size: int
