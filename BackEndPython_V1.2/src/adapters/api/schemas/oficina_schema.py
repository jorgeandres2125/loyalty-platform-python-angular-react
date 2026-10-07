from __future__ import annotations

from pydantic import BaseModel


class OficinaResponse(BaseModel):
    cod_oficinas: int | None = None
    id_oficinas: int | None = None
    nom_oficinas: str = ""
    marca: str = ""
    regional: str = ""
    cpid: int | None = None
    ind_activo: bool | None = None
