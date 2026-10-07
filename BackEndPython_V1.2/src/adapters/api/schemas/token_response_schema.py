from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.modulo_permiso_schema import ModuloPermisoSchema


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str
    token_type: str = "bearer"
    uid: int
    username: str
    email: str
    roles: list[str] = []
    modulos: list[ModuloPermisoSchema] = []
