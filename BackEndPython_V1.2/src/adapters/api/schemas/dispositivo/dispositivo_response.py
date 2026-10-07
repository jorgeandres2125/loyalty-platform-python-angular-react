from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DispositivoResponse(BaseModel):
    """AP-0014: un dispositivo (equipo origen) desde el que el usuario se ha autenticado."""

    model_config = ConfigDict(extra="forbid")

    device_hash: str
    device_name: str
    user_agent: str
    first_login: str
    last_login: str
    veces_visto: int
    trusted: bool
