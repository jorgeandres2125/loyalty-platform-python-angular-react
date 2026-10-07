from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CanalFormDTO:
    """DTO para crear o actualizar un canal (tabla canales + canales_oficinas)."""
    nom_canales: str
    cpid: int | None
    cspid: int | None
    ind_activo: bool
    id_canales: int = 0  # auto-generado en crear_async; ignorado en actualizar_async
    oficinas_ids: list[int] = field(default_factory=list)
