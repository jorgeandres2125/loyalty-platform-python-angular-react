from __future__ import annotations

from pydantic import BaseModel


class SubprogramaItem(BaseModel):
    cspid: int | None = None
    cspid_nombre: str | None = None
