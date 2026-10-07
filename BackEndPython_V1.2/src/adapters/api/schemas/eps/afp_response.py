from __future__ import annotations

from pydantic import BaseModel


class AfpResponse(BaseModel):
    tid: int
    nombre: str
    nit: str | None = None
