from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.admin.ciudades.ciudad_list_item import CiudadListItem


class CiudadListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[CiudadListItem]
    total: int
    page: int
    page_size: int
