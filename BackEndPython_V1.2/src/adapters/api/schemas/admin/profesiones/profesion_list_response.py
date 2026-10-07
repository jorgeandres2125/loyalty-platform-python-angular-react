from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.admin.profesiones.profesion_list_item import (
    ProfesionListItem,
)


class ProfesionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[ProfesionListItem]
    total: int
    page: int
    page_size: int
