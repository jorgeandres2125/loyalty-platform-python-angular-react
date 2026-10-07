from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OficinaListItemDTO:
    cod_oficinas: int
    id_oficinas: int | None
    nom_oficinas: str
    marca: str
    regional: str
    cpid: int | None
    ind_activo: bool
    ciudad_nombre: str = ""
    did: int | None = None
    departamento_nombre: str = ""
