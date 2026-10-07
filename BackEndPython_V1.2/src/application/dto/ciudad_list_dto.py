from __future__ import annotations

from dataclasses import dataclass

from src.application.dto.ciudad_list_item_dto import CiudadListItemDTO


@dataclass
class CiudadListDTO:
    items: list[CiudadListItemDTO]
    total: int
    page: int
    page_size: int
