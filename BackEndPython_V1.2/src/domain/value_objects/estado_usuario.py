from enum import Enum


class EstadoUsuario(str, Enum):
    """AP-0133: estado del usuario que determina si puede realizar acciones.

    ACTIVO opera con normalidad; los demas son estados de acceso denegado que el
    ValidadorSesion rechaza en CADA peticion (401 o 403), aunque el JWT siga vigente.
    INHABILITADO es la deshabilitacion administrativa (AP-0001); BLOQUEADO es el bloqueo
    por intentos fallidos (AP-0009); ELIMINADO es la baja logica o la ausencia de la
    cuenta (AP-0049)."""

    ACTIVO = "activo"
    INHABILITADO = "inhabilitado"
    BLOQUEADO = "bloqueado"
    ELIMINADO = "eliminado"
