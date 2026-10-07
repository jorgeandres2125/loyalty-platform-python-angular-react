from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CanalFormResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cod_canales: int
    nom_canales: str
    cpid: int | None
    cspid: int | None
    ind_activo: bool
    id_canales: int
    oficinas_ids: list[int] = Field(default_factory=list)
