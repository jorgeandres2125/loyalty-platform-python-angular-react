from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CiudadFormResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cid: int
    did: int | None = None
    ciudad: str
