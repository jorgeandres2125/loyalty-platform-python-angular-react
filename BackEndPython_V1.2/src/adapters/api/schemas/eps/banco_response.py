from __future__ import annotations

from pydantic import BaseModel


class BancoResponse(BaseModel):
    tid: int
    nombre: str
    codigo: str | None = None
