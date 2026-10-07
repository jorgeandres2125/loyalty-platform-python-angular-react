from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class DocumentoEditRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Annotated[str | None, Field(default=None, max_length=200)] = None
    estado: Annotated[str | None, Field(default=None, max_length=20)] = None
    fecha: datetime | None = None
