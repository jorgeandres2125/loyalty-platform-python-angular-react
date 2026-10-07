from __future__ import annotations

from pydantic import BaseModel


class CanalResponse(BaseModel):
    cod_canales: int | None = None
    nom_canales: str = ""
    cpid: int | None = None
    cspid: int | None = None
    ind_activo: bool | None = None
    id_canales: int = 0
