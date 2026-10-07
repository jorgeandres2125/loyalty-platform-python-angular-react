from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OficinaActivaItem(BaseModel):
    """Item compacto para listas desplegables (TomSelect / autocomplete)."""

    model_config = ConfigDict(extra="forbid")

    cod_oficinas: int
    nom_oficinas: str
