from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RolDeUsuarioResponse(BaseModel):
    """Rol del sistema con la marca de si está asignado al usuario consultado."""

    model_config = ConfigDict(extra="forbid")

    rid: int
    name: str
    asignado: bool
