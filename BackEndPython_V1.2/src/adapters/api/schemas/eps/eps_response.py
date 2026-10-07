from __future__ import annotations

from pydantic import BaseModel


class EpsResponse(BaseModel):
    tid: int
    nombre: str
    nit: str | None = None
