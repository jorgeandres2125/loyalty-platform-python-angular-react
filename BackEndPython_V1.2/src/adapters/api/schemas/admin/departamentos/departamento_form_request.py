from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class DepartamentoFormRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    departamento: Annotated[str, Field(min_length=1, max_length=50)]
    pid: int | None = None
