from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OficinaFormDTO:
    """DTO para crear o actualizar una oficina (tabla oficinas + canales_oficinas)."""
    nom_oficinas: str
    marca: str
    regional: str
    cpid: int | None
    ind_activo: bool
    id_oficinas: int | None = None  # auto-generado en crear_async; ignorado en actualizar_async
    canales_ids: list[int] = field(default_factory=list)
