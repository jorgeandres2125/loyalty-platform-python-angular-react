from __future__ import annotations

from dataclasses import dataclass

from src.application.dto.usuario_list_item_dto import UsuarioListItemDTO


@dataclass
class UsuarioListDTO:
    items: list[UsuarioListItemDTO]
    total: int
    page: int
    page_size: int
