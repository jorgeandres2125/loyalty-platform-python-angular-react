from __future__ import annotations

from dataclasses import dataclass

from src.application.dto.oficina_list_item_dto import OficinaListItemDTO


@dataclass
class OficinaListDTO:
    items: list[OficinaListItemDTO]
    total: int
    page: int
    page_size: int
