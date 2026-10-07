from __future__ import annotations

from pydantic import BaseModel


class RegistroAuditoriaResponse(BaseModel):
    """AP-0028: un asiento del historial de auditoria expuesto al usuario."""

    id: int | None
    accion: str
    entidad: str | None
    entidad_id: str | None
    detalle: str | None
    ip_origen: str | None
    resultado: str
    creado_en: str
