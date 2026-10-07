from __future__ import annotations

import os
from typing import Final

from fastapi import APIRouter

from src.adapters.api.schemas.debug.database_settings_view import DatabaseSettingsView
from src.adapters.api.schemas.debug.jwt_settings_view import JwtSettingsView
from src.adapters.api.schemas.debug.sapin_settings_view import SapinSettingsView
from src.adapters.api.schemas.debug.settings_debug_response import SettingsDebugResponse
from src.infrastructure.config.dependencies import SettingsDep
from src.infrastructure.config.settings import _ENV_FILES

router: APIRouter = APIRouter()

_JWT_PLACEHOLDERS: Final[frozenset[str]] = frozenset(
    {"CHANGE-ME-IN-PRODUCTION", "changeme", "change-me", "secret", "your-secret-key", "Admin123*"}
)


@router.get(
    "/settings",
    response_model=SettingsDebugResponse,
    summary="Vista efectiva de Settings (registrado solo cuando debug=True)",
)
async def vista_settings(settings: SettingsDep) -> SettingsDebugResponse:
    """Diagnóstico de configuracion cargada. Secretos redactados (longitud, no valor)."""
    return SettingsDebugResponse(
        app_env=settings.app_env,
        debug=settings.debug,
        env_files=list(_ENV_FILES),
        env_files_existen=[os.path.exists(f) for f in _ENV_FILES],
        log_level=settings.log_level,
        log_format=settings.log_format,
        cors_origins=settings.cors_origins,
        jwt=JwtSettingsView(
            algorithm=settings.jwt_algorithm,
            expire_minutes=settings.jwt_expire_minutes,
            secret_key_length=len(settings.jwt_secret_key),
            secret_key_is_default=(
                not settings.jwt_secret_key
                or settings.jwt_secret_key in _JWT_PLACEHOLDERS
            ),
        ),
        database=DatabaseSettingsView(
            host=settings.db_host,
            port=settings.db_port,
            name=settings.db_name,
            user=settings.db_user,
            driver=settings.db_driver,
            password_length=len(settings.db_password),
            pool_min=settings.db_pool_min,
            pool_max=settings.db_pool_max,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=settings.db_pool_recycle,
        ),
        sapin=SapinSettingsView(
            url=settings.sapin_url,
            aes_key_ctr_configured=bool(settings.sapin_aes_key_ctr),
            aes_iv_ctr_configured=bool(settings.sapin_aes_iv_ctr),
            aes_key_cbc_configured=bool(settings.sapin_aes_key_cbc),
        ),
    )
