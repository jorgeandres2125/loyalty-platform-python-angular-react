from __future__ import annotations

from dataclasses import dataclass

from src.application.dto.banco_list_item_dto import BancoListItemDTO


@dataclass
class BancoListDTO:
    items: list[BancoListItemDTO]
    total: int
    page: int
    page_size: int
