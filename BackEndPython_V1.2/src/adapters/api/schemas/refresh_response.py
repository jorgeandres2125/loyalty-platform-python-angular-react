from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RefreshResponse(BaseModel):
    """AP-0129: respuesta de la renovacion de sesion por actividad. Informa al cliente el
    nuevo token y cuantos segundos de inactividad quedan antes de expirar."""

    model_config = ConfigDict(extra="forbid")

    access_token: str
    token_type: str = "bearer"
    expira_en_seg: int
    canal: bool
