from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.admin.bancos.banco_list_item import BancoListItem


class BancoListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[BancoListItem]
    total: int
    page: int
    page_size: int
