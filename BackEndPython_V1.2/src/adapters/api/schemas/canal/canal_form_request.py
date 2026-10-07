from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class CanalFormRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nom_canales: Annotated[str, Field(min_length=1, max_length=120)]
    cpid: int | None = None
    cspid: int | None = None
    ind_activo: bool = True
    oficinas_ids: list[int] = Field(default_factory=list)
