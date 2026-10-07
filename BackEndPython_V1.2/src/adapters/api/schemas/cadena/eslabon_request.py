from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EslabonRequest(BaseModel):
    """AP-0025: un eslabon de la cadena de sellos enviado para su verificacion."""

    model_config = ConfigDict(extra="forbid")

    secuencia: int = Field(ge=0)
    hash_previo: str = Field(min_length=64, max_length=64)
    hash_contenido: str = Field(min_length=64, max_length=64)
    hash_actual: str = Field(min_length=64, max_length=64)
