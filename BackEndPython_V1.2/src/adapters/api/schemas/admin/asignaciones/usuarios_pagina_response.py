from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.admin.asignaciones.usuario_cuenta_response import (
    UsuarioCuentaResponse,
)


class UsuariosPaginaResponse(BaseModel):
    """Página de cuentas de usuario."""

    model_config = ConfigDict(extra="forbid")

    items: list[UsuarioCuentaResponse]
    total: int
    page: int
    page_size: int
