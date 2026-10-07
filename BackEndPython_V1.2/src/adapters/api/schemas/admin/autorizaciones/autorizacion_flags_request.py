from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AutorizacionFlagsRequest(BaseModel):
    """Cuerpo para actualizar los 6 flags de un rol sobre un módulo (AP-0054)."""
    model_config = ConfigDict(extra="forbid")

    puede_ver: bool
    puede_crear: bool
    puede_editar: bool
    puede_eliminar: bool
    puede_exportar: bool
    puede_aprobar: bool
