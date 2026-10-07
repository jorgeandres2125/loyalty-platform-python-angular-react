from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class CiudadFormRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ciudad: Annotated[str, Field(min_length=1, max_length=50)]
    did: int | None = None
