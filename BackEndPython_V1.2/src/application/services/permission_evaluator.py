from __future__ import annotations

from src.domain.value_objects.permiso import Permiso
from src.domain.value_objects.regla_acceso import ReglaAcceso


class PermissionEvaluator:
    """AP-0055: evalua la capa RBAC de una regla de acceso contra los permisos
    efectivos del actor (deny-by-default cuando la regla declara permisos)."""

    def permite_rol(
        self, permisos_efectivos: frozenset[Permiso], regla: ReglaAcceso
    ) -> bool:
        if not regla.permisos:
            return True
        return bool((regla.permisos | regla.staff_bypass) & permisos_efectivos)

    def es_staff(
        self, permisos_efectivos: frozenset[Permiso], regla: ReglaAcceso
    ) -> bool:
        return bool(regla.staff_bypass & permisos_efectivos)
