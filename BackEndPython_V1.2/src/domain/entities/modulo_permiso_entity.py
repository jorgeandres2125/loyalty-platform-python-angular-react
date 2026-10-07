from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModuloPermisoEntity:
    """Permisos efectivos del usuario sobre un módulo del frontend.

    Resultado de la unión (OR) de los permisos otorgados por todos los roles
    del usuario sobre el módulo. Inmutable: representa un snapshot por request.
    """
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
