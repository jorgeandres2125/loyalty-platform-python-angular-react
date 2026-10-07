from __future__ import annotations

from fastapi import APIRouter

from src.adapters.api.schemas.config.upload_limits_response import UploadLimitsResponse
from src.infrastructure.config.dependencies import SettingsDep

router = APIRouter()

_BYTES_POR_MB: int = 1_048_576


@router.get("/uploads", response_model=UploadLimitsResponse)
async def obtener_limites_upload(settings: SettingsDep) -> UploadLimitsResponse:
    """AP-0137: expone el tamano maximo de subida para que el frontend lo use
    como referencia al limitar los archivos antes de enviarlos."""
    return UploadLimitsResponse(
        max_upload_bytes=settings.max_upload_bytes,
        max_upload_mb=round(settings.max_upload_bytes / _BYTES_POR_MB, 2),
    )
