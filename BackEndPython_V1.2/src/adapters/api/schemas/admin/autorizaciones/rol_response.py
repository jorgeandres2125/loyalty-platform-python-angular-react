from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RolResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rid: int
    name: str
