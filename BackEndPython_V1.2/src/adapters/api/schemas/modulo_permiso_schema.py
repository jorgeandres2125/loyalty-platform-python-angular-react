from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ModuloPermisoSchema(BaseModel):
    """Un módulo del frontend con los permisos efectivos del usuario sobre él."""
    model_config = ConfigDict(extra="forbid")

    module_id: int
    module_code: str
    nombre: str
    ruta: str | None
    icono: str | None
    orden: int
    puede_ver: bool
    puede_crear: bool
    puede_editar: bool
    puede_eliminar: bool
    puede_exportar: bool
    puede_aprobar: bool
