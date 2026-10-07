from __future__ import annotations

from dataclasses import dataclass

from src.application.dto.departamento_list_item_dto import DepartamentoListItemDTO


@dataclass
class DepartamentoListDTO:
    items: list[DepartamentoListItemDTO]
    total: int
    page: int
    page_size: int
