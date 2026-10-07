from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CanalListItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cod_canales: int
    nom_canales: str
    cpid: int | None
    cspid: int | None
    ind_activo: bool
    id_canales: int
