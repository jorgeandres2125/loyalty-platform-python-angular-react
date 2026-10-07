from __future__ import annotations

from dataclasses import dataclass

from src.application.dto.admin_subprograma_list_item_dto import (
    AdminSubprogramaListItemDTO,
)


@dataclass
class AdminSubprogramaListDTO:
    items: list[AdminSubprogramaListItemDTO]
    total: int
    page: int
    page_size: int
