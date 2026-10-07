from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.canal.canal_list_item import CanalListItem


class CanalListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[CanalListItem]
    total: int
    page: int
    page_size: int
