from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AutorizacionModuloResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    rid: int
    module_id: int
    module_code: str
    module_nombre: str
    module_icono: str
    module_activo: bool
    permission_id: int
    puede_ver: bool
    puede_crear: bool
    puede_editar: bool
    puede_eliminar: bool
    puede_exportar: bool
    puede_aprobar: bool
