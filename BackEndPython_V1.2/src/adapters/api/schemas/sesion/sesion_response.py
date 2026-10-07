from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SesionResponse(BaseModel):
    """AP-0130: una sesion activa del usuario en el Session Registry, para la pantalla
    'Mis sesiones'. El sid es un identificador opaco de gestion (no es el JWT ni un
    secreto); permite cerrar la sesion mediante DELETE sin exponer el token."""

    model_config = ConfigDict(extra="forbid")

    sid: str
    ip: str
    user_agent: str
    canal: bool
    inicio: str
    last_activity: str
    es_actual: bool
