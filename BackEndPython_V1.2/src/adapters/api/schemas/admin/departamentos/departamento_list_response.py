from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.admin.departamentos.departamento_list_item import (
    DepartamentoListItem,
)


class DepartamentoListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[DepartamentoListItem]
    total: int
    page: int
    page_size: int
