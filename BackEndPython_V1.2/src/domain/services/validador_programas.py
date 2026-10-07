from src.domain.exceptions.programa_no_autorizado import ProgramaNoAutorizado
from src.domain.value_objects.rol_usuario import RolUsuario

_ROLES_MOVILIDAD = {
    RolUsuario.COMISIONISTA,
    RolUsuario.ASESOR_COMERCIAL,
    RolUsuario.ASESOR_CALLCENTER,
    RolUsuario.TELEPERFORMANCE,
    RolUsuario.EJECUTIVO_MOVILIDAD_CONSUMO,
}

_ROLES_CONSUMO = {
    RolUsuario.COMISIONISTA_CONSUMO,
    RolUsuario.ASESOR_CONSUMO,
    RolUsuario.EJECUTIVO_CONSUMO,
    RolUsuario.EJECUTIVO_MOVILIDAD_CONSUMO,
}


def validar_acceso_programa(roles: list[RolUsuario], programa: str) -> None:
    """Lanza ProgramaNoAutorizado si ningún rol tiene acceso al programa indicado."""
    if RolUsuario.ADMINISTRATOR in roles or RolUsuario.WEBMASTER in roles:
        return
    if programa == "movilidad" and not any(rol in _ROLES_MOVILIDAD for rol in roles):
        raise ProgramaNoAutorizado(programa)
    if programa == "consumo" and not any(rol in _ROLES_CONSUMO for rol in roles):
        raise ProgramaNoAutorizado(programa)
