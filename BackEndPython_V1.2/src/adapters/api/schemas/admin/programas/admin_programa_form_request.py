from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class AdminProgramaFormRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cp_nombre: Annotated[str, Field(min_length=1, max_length=50)]
