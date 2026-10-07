from __future__ import annotations

from pydantic import BaseModel


class OficinaItem(BaseModel):
    cod_oficinas: int | None = None
    id_oficinas: int | None = None
    nom_oficinas: str | None = None
