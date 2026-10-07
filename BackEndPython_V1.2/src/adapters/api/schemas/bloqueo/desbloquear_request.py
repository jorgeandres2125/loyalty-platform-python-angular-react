from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DesbloquearRequest(BaseModel):
    """AP-0009: desbloqueo manual de una cuenta por un administrador."""

    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=120)
