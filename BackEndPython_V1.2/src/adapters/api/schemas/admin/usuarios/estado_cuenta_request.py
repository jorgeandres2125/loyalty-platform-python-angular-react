from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class EstadoCuentaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activo: bool
    motivo: Annotated[str | None, Field(default=None, max_length=255)]
