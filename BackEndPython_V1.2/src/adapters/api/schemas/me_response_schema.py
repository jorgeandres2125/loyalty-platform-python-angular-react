from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.modulo_permiso_schema import ModuloPermisoSchema
from src.adapters.api.schemas.password_aviso_schema import PasswordAvisoSchema


class MeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    uid: int
    username: str
    email: str
    roles: list[str]
    tiene_incentivos: bool
    programa: int | None
    modulos: list[ModuloPermisoSchema] = []
    # AP-0037: aviso de vencimiento de contrasena; null salvo dentro de la ventana.
    password_aviso: PasswordAvisoSchema | None = None
    # AP-0132: instante absoluto de expiracion de la sesion (no secreto), para que el
    # cliente anticipe el cierre y descarte sus datos locales. ISO 8601 o null.
    session_expires_at: str | None = None
