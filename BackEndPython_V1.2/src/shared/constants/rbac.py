"""Politica RBAC: mapa canonico rol -> permisos (AP-0053).

Fuente unica de autorizacion del stack. Reconciliable con dbo.role_permission
(spec 17). `administrator` es superusuario (todos los permisos). Los conjuntos de
los guardias legacy (require_admin_*) se reproducen exactamente para no alterar los
controles ya en verde (AP-0001, catalogos).
"""
from typing import Final

from src.domain.value_objects.permiso import Permiso
from src.domain.value_objects.rol_usuario import RolUsuario

_TODOS: Final[frozenset[Permiso]] = frozenset(Permiso)

# Conjuntos de roles reutilizados (staff que opera sobre comisionistas).
_STAFF_ASESORES: Final[frozenset[RolUsuario]] = frozenset(
    {
        RolUsuario.ASESOR_LOGISTICO,
        RolUsuario.ASESOR_COMERCIAL,
        RolUsuario.ASESOR_CALLCENTER,
        RolUsuario.ASESOR_CONSUMO,
        RolUsuario.EJECUTIVO_CONSUMO,
        RolUsuario.EJECUTIVO_MOVILIDAD_CONSUMO,
    }
)

ROL_PERMISOS: Final[dict[RolUsuario, frozenset[Permiso]]] = {
    # Superusuario y webmaster
    RolUsuario.ADMINISTRATOR: _TODOS,
    RolUsuario.WEBMASTER: frozenset(
        {
            Permiso.USUARIOS_GESTIONAR_ESTADO,
            Permiso.COMISIONISTAS_GESTIONAR_ESTADO,
            Permiso.AUTORIZACIONES_GESTIONAR,
            Permiso.ASIGNACIONES_GESTIONAR,
            Permiso.INACTIVACION_AUTORIZAR,
            Permiso.MOVILIDAD_ASESORES_GESTIONAR,
            Permiso.CONSUMO_ASESORES_GESTIONAR,
            Permiso.DOCUMENTOS_MODERAR,
            Permiso.REPORTES_EXPORTAR,
            Permiso.INCENTIVOS_GESTIONAR,
            Permiso.CATALOGOS_REFERENCIA_VER,
            Permiso.CATALOGOS_REFERENCIA_GESTIONAR,
            Permiso.DISPOSITIVOS_VER_PROPIO,
            Permiso.AUDITORIA_VER_PROPIO,
            Permiso.FIRMA_GESTIONAR,
            Permiso.OOB_AUTORIZAR,
            Permiso.USUARIOS_SOFTLOCK_GESTIONAR,
        }
    ),
    # Documentador: modera documentos y opera catalogos de referencia
    RolUsuario.DOCUMENTADOR: frozenset(
        {
            Permiso.DOCUMENTOS_MODERAR,
            Permiso.CATALOGOS_REFERENCIA_VER,
            Permiso.DISPOSITIVOS_VER_PROPIO,
            Permiso.AUDITORIA_VER_PROPIO,
        }
    ),
    # Comisionista Movilidad (usuario final)
    RolUsuario.COMISIONISTA: frozenset(
        {
            Permiso.MOVILIDAD_PERFIL_VER_PROPIO,
            Permiso.DOCUMENTOS_SUBIR_PROPIO,
            Permiso.CATALOGOS_REFERENCIA_VER,
            Permiso.DISPOSITIVOS_VER_PROPIO,
            Permiso.AUDITORIA_VER_PROPIO,
            Permiso.OOB_AUTORIZAR,
        }
    ),
    # Comisionista Consumo (usuario final)
    RolUsuario.COMISIONISTA_CONSUMO: frozenset(
        {
            Permiso.CONSUMO_PERFIL_VER_PROPIO,
            Permiso.DOCUMENTOS_SUBIR_PROPIO,
            Permiso.CATALOGOS_REFERENCIA_VER,
            Permiso.DISPOSITIVOS_VER_PROPIO,
            Permiso.AUDITORIA_VER_PROPIO,
            Permiso.OOB_AUTORIZAR,
        }
    ),
    RolUsuario.TELEPERFORMANCE: frozenset(
        {
            Permiso.CATALOGOS_REFERENCIA_VER,
            Permiso.DISPOSITIVOS_VER_PROPIO,
            Permiso.AUDITORIA_VER_PROPIO,
        }
    ),
}

# Staff de asesores: gestion de asesores, documentos, reportes y catalogos.
_PERMISOS_STAFF: Final[frozenset[Permiso]] = frozenset(
    {
        Permiso.COMISIONISTAS_GESTIONAR_ESTADO,
        Permiso.MOVILIDAD_ASESORES_GESTIONAR,
        Permiso.CONSUMO_ASESORES_GESTIONAR,
        Permiso.DOCUMENTOS_MODERAR,
        Permiso.REPORTES_EXPORTAR,
        Permiso.INCENTIVOS_GESTIONAR,
        Permiso.CATALOGOS_REFERENCIA_VER,
        Permiso.CATALOGOS_REFERENCIA_GESTIONAR,
        Permiso.DISPOSITIVOS_VER_PROPIO,
        Permiso.AUDITORIA_VER_PROPIO,
        Permiso.FIRMA_GESTIONAR,
        Permiso.OOB_AUTORIZAR,
    }
)
for _rol in _STAFF_ASESORES:
    ROL_PERMISOS[_rol] = _PERMISOS_STAFF


def permisos_de_roles(roles: frozenset[RolUsuario]) -> frozenset[Permiso]:
    """Union de los permisos efectivos de un conjunto de roles (deny-by-default:
    roles sin entrada aportan cero permisos)."""
    efectivos: set[Permiso] = set()
    for rol in roles:
        efectivos |= ROL_PERMISOS.get(rol, frozenset())
    return frozenset(efectivos)
