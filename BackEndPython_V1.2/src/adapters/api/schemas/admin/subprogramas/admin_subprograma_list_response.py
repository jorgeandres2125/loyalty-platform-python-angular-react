from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.admin.subprogramas.admin_subprograma_list_item import (
    AdminSubprogramaListItem,
)


class AdminSubprogramaListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[AdminSubprogramaListItem]
    total: int
    page: int
    page_size: int
