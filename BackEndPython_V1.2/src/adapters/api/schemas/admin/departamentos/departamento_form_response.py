from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DepartamentoFormResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    did: int
    pid: int | None = None
    departamento: str
