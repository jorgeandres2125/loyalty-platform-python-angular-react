from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class JwtSettingsView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    algorithm: str
    expire_minutes: int
    secret_key_length: int
    secret_key_is_default: bool
