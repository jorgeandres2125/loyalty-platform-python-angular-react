from __future__ import annotations

from dataclasses import dataclass

from src.application.dto.profesion_list_item_dto import ProfesionListItemDTO


@dataclass
class ProfesionListDTO:
    items: list[ProfesionListItemDTO]
    total: int
    page: int
    page_size: int
