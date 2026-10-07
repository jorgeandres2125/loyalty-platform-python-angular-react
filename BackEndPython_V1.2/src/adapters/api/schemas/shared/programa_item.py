from __future__ import annotations

from pydantic import BaseModel


class ProgramaItem(BaseModel):
    cpid: int | None = None
    cp_nombre: str | None = None
