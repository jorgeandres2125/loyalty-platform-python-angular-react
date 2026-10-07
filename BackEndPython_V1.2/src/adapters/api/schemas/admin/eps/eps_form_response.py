from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class EpsFormResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tid: int
    nombre: str
    nit: str | None = None
