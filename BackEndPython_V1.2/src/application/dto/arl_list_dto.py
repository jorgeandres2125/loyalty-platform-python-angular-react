from __future__ import annotations

from dataclasses import dataclass

from src.application.dto.arl_list_item_dto import ArlListItemDTO


@dataclass
class ArlListDTO:
    items: list[ArlListItemDTO]
    total: int
    page: int
    page_size: int
