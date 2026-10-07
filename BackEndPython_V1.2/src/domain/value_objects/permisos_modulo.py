from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PermisosModulo:
    """Los 6 flags de permiso de un rol sobre un módulo (AP-0054).

    Value object inmutable que viaja entre el caso de uso y el repositorio sin
    arrastrar dependencias de framework ni de la capa de aplicación al dominio.
    """
    puede_ver: bool = False
    puede_crear: bool = False
    puede_editar: bool = False
    puede_eliminar: bool = False
    puede_exportar: bool = False
    puede_aprobar: bool = False

    @property
    def tiene_alguna_accion(self) -> bool:
        """Cualquier acción distinta de 'ver' (crear/editar/eliminar/exportar/aprobar)."""
        return (
            self.puede_crear
            or self.puede_editar
            or self.puede_eliminar
            or self.puede_exportar
            or self.puede_aprobar
        )
