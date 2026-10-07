from __future__ import annotations

from dataclasses import dataclass

from src.application.dto.ejecutivo_list_item_dto import EjecutivoListItemDTO


@dataclass
class EjecutivoListDTO:
    items: list[EjecutivoListItemDTO]
    total: int
    page: int
    page_size: int
