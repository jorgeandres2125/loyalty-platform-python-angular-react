from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ProfesionFormRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Annotated[str, Field(min_length=1, max_length=220)]
