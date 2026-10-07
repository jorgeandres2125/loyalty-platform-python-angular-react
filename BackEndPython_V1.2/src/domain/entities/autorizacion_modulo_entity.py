from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AutorizacionModuloEntity:
    rid: int = 0
    module_id: int = 0
    module_code: str = ""
    module_nombre: str = ""
    module_icono: str = ""
    module_activo: bool = False
    permission_id: int = 0
    puede_ver: bool = False
    puede_crear: bool = False
    puede_editar: bool = False
    puede_eliminar: bool = False
    puede_exportar: bool = False
    puede_aprobar: bool = False
