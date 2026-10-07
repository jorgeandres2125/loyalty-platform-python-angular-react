from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class UsuarioListItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    uid: int
    nombre: str
    email: str
    activo: bool
    roles: list[str] = []
