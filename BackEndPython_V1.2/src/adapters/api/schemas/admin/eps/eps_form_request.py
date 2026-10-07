from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class EpsFormRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Annotated[str, Field(min_length=1, max_length=200)]
    nit: Annotated[str | None, Field(default=None, max_length=30)]
