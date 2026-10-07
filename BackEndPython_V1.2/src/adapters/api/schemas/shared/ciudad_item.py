from __future__ import annotations

from pydantic import BaseModel


class CiudadItem(BaseModel):
    cid: int
    did: int | None = None
    ciudad: str
