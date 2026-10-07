from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class EstadoDisponibilidadResponse(BaseModel):
    """AP-0081: respuesta de las sondas de disponibilidad (liveness/readiness) que
    consumen Kubernetes, el balanceador y el monitoreo de alta disponibilidad."""

    model_config = ConfigDict(extra="forbid")

    estado: str
    version: str
    base_datos: bool | None = None
