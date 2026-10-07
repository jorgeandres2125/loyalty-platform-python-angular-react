from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TokenOAuthRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audience: str = Field(min_length=1, max_length=50, description="App de terceros, ej. sapin")
    scope: str | None = Field(default=None, max_length=200)
