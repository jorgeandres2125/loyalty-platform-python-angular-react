from __future__ import annotations

from pydantic import BaseModel


class ProfesionResponse(BaseModel):
    tid: int
    nombre: str
