from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CanalActivaItem(BaseModel):
    """Item compacto para listas desplegables (TomSelect / autocomplete)."""

    model_config = ConfigDict(extra="forbid")

    cod_canales: int
    nom_canales: str
