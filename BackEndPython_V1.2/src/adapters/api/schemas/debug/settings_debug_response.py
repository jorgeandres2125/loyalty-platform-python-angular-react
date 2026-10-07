from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.debug.database_settings_view import DatabaseSettingsView
from src.adapters.api.schemas.debug.jwt_settings_view import JwtSettingsView
from src.adapters.api.schemas.debug.sapin_settings_view import SapinSettingsView


class SettingsDebugResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app_env: str
    debug: bool
    env_files: list[str]
    env_files_existen: list[bool]
    log_level: str
    log_format: str
    cors_origins: list[str]
    jwt: JwtSettingsView
    database: DatabaseSettingsView
    sapin: SapinSettingsView
