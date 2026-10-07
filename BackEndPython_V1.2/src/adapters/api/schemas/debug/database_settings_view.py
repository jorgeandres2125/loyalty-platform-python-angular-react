from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DatabaseSettingsView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host: str
    port: int
    name: str
    user: str
    driver: str
    password_length: int
    pool_min: int
    pool_max: int
    pool_timeout: int
    pool_recycle: int
