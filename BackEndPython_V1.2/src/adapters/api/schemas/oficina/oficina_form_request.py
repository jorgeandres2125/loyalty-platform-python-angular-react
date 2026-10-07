from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class OficinaFormRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nom_oficinas: Annotated[str, Field(min_length=1, max_length=120)]
    marca: Annotated[str, Field(default="", max_length=45)] = ""
    regional: Annotated[str, Field(default="", max_length=45)] = ""
    cpid: int | None = None
    ind_activo: bool = True
    canales_ids: list[int] = Field(default_factory=list)
