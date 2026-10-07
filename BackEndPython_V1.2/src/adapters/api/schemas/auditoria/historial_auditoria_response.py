from __future__ import annotations

from pydantic import BaseModel

from src.adapters.api.schemas.auditoria.registro_auditoria_response import (
    RegistroAuditoriaResponse,
)


class HistorialAuditoriaResponse(BaseModel):
    """AP-0028: pagina del historial de auditoria del propio usuario."""

    items: list[RegistroAuditoriaResponse]
    page: int
    page_size: int
    total: int
