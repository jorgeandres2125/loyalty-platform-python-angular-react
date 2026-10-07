from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AdminProgramaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cpid: int
    cp_nombre: str
