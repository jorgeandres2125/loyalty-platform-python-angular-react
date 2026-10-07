from __future__ import annotations

from pydantic import BaseModel


class ArlResponse(BaseModel):
    tid: int
    nombre: str
    nit: str | None = None
