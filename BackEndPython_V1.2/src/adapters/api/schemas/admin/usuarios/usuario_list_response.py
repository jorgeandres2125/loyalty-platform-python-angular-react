from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.admin.usuarios.usuario_list_item import UsuarioListItem


class UsuarioListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[UsuarioListItem]
    total: int
    page: int
    page_size: int
