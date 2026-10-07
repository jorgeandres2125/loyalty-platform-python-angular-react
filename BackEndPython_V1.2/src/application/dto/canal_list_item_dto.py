from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CanalListItemDTO:
    cod_canales: int
    nom_canales: str
    cpid: int | None
    cspid: int | None
    ind_activo: bool
    id_canales: int
