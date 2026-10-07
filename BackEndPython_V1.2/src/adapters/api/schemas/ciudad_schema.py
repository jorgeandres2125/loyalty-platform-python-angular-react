from __future__ import annotations

from pydantic import BaseModel


class CiudadResponse(BaseModel):
    cid: int
    did: int
    ciudad: str
