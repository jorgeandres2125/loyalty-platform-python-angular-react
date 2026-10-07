from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.admin.afp.afp_list_item import AfpListItem


class AfpListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[AfpListItem]
    total: int
    page: int
    page_size: int
