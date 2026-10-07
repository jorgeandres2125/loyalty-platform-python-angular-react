from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CanalEntity:
    """Canal de distribución — tabla canales (+ relación N:M canales_oficinas)."""
    cod_canales: int | None = None
    nom_canales: str = ""
    cpid: int | None = None
    cspid: int | None = None
    ind_activo: bool | None = None
    id_canales: int = 0
    oficinas_ids: list[int] = field(default_factory=list)
