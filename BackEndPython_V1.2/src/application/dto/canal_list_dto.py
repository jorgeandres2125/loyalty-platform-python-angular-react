from __future__ import annotations

from dataclasses import dataclass

from src.application.dto.canal_list_item_dto import CanalListItemDTO


@dataclass
class CanalListDTO:
    items: list[CanalListItemDTO]
    total: int
    page: int
    page_size: int
