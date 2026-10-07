from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OficinaFormResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cod_oficinas: int
    id_oficinas: int | None
    nom_oficinas: str
    marca: str
    regional: str
    cpid: int | None
    ind_activo: bool
    ciudad_nombre: str
    did: int | None
    departamento_nombre: str
    canales_ids: list[int] = Field(default_factory=list)
