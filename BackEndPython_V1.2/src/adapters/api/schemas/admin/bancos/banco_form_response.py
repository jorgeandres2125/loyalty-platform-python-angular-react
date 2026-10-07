from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BancoFormResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tid: int
    nombre: str
    codigo: str | None = None
