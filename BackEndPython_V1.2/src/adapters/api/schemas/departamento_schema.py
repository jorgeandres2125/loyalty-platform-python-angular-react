from __future__ import annotations

from pydantic import BaseModel


class DepartamentoResponse(BaseModel):
    did: int
    pid: int
    departamento: str
