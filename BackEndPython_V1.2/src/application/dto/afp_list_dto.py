from __future__ import annotations

from dataclasses import dataclass

from src.application.dto.afp_list_item_dto import AfpListItemDTO


@dataclass
class AfpListDTO:
    items: list[AfpListItemDTO]
    total: int
    page: int
    page_size: int
