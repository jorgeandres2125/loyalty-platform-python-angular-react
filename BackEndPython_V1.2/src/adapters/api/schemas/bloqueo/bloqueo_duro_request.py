from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BloqueoDuroRequest(BaseModel):
    """AP-0157: aplicacion de un bloqueo duro (administrativo o de seguridad) a una cuenta."""

    model_config = ConfigDict(extra="forbid")

    motivo: str = Field(min_length=1, max_length=400)
