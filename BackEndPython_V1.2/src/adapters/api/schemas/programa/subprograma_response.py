from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SubprogramaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cspid: int
    cspid_nombre: str
    cpid: int | None
