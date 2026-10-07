from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.adapters.api.schemas.cadena.eslabon_request import EslabonRequest


class VerificarCadenaRequest(BaseModel):
    """AP-0025: peticion para verificar la integridad de una cadena de sellos."""

    model_config = ConfigDict(extra="forbid")

    eslabones: list[EslabonRequest] = Field(min_length=1, max_length=100000)
