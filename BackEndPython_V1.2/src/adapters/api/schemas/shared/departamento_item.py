from __future__ import annotations

from pydantic import BaseModel


class DepartamentoItem(BaseModel):
    did: int
    pid: int | None = None
    departamento: str
