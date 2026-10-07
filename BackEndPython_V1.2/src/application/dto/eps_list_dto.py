from __future__ import annotations

from dataclasses import dataclass

from src.application.dto.eps_list_item_dto import EpsListItemDTO


@dataclass
class EpsListDTO:
    items: list[EpsListItemDTO]
    total: int
    page: int
    page_size: int
