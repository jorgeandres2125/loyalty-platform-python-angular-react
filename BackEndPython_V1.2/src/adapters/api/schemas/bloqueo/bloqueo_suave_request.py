from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BloqueoSuaveRequest(BaseModel):
    """AP-0157: aplicacion administrativa de un bloqueo suave (temporal/operativo).

    Distinto del bloqueo suave AUTOMATICO por intentos fallidos (AP-0009): este lo aplica
    un operador con motivo y una duracion en minutos, tras la cual expira."""

    model_config = ConfigDict(extra="forbid")

    motivo: str = Field(min_length=1, max_length=400)
    duracion_minutos: int = Field(gt=0, le=10080)
