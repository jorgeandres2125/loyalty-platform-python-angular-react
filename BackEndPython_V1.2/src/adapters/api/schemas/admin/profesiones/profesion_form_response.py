from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ProfesionFormResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tid: int
    nombre: str
