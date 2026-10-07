from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PasswordTemporalResponse(BaseModel):
    """AP-0047 y AP-0048: resultado de la emision de una contrasena temporal.

    password_temporal viaja en claro UNICAMENTE en esta respuesta (se muestra una
    sola vez al emisor); el sistema solo persiste su hash bcrypt.
    """

    model_config = ConfigDict(extra="forbid")

    uid: int
    usuario: str
    password_temporal: str
    expira_iso: str
    ttl_minutos: int
