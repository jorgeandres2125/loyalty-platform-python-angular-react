from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AdminSubprogramaListItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cspid: int
    cspid_nombre: str
    cpid: int | None = None
