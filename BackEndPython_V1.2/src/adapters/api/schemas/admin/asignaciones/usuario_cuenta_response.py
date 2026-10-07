from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class UsuarioCuentaResponse(BaseModel):
    """Cuenta de usuario en las vistas de asignación de roles."""

    model_config = ConfigDict(extra="forbid")

    uid: int
    nombre: str
    email: str
    activo: bool
