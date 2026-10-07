from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RolAsignableResponse(BaseModel):
    """Rol del sistema que puede asignarse a usuarios (excluye roles técnicos)."""

    model_config = ConfigDict(extra="forbid")

    rid: int
    name: str
