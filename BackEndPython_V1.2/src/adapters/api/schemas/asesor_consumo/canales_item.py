from __future__ import annotations

from pydantic import BaseModel


class CanalesItem(BaseModel):
    cod_canales: int | None = None
    nom_canales: str | None = None
