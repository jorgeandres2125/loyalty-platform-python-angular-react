from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Final

from fastapi import HTTPException, status

from src.domain.value_objects.permiso import Permiso
from src.domain.value_objects.rol_usuario import RolUsuario
from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.infrastructure.config.dependencies import SettingsDep, TokenDep
from src.shared.constants.eventos_seguridad import (
    EVENTO_AUTORIZACION,
    LOGGER_SEGURIDAD,
    RESULTADO_FALLO,
)
from src.shared.constants.rbac import permisos_de_roles

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)

MODO_ENFORCE: Final[str] = "enforce"
MODO_AUDIT: Final[str] = "audit"


def _roles_de_token(token: dict) -> frozenset[RolUsuario]:
    """Roles conocidos del JWT; los desconocidos se ignoran (no aportan permisos)."""
    roles: set[RolUsuario] = set()
    for valor in token.get("roles") or []:
        try:
            roles.add(RolUsuario(str(valor)))
        except ValueError:
            pass
    return frozenset(roles)


def actor_desde_token(token: dict) -> tuple[int, list[RolUsuario]]:
    """Extrae (uid, roles) del JWT decodificado. El claim 'sub' es el uid como str
    y 'roles' es la lista de valores de RolUsuario."""
    actor_uid: int = int(token["sub"])
    return actor_uid, list(_roles_de_token(token))


def _tiene_alguno(token: dict, requeridos: frozenset[Permiso]) -> bool:
    efectivos: frozenset[Permiso] = permisos_de_roles(_roles_de_token(token))
    return bool(requeridos & efectivos)


def _auditar_denegacion(token: dict, requeridos: frozenset[Permiso], modo: str) -> None:
    _logger.warning(
        "AP-0053: autorizacion denegada",
        extra={
            "evento_seguridad": EVENTO_AUTORIZACION,
            "severidad": SeveridadSeguridad.ALTA.value,
            "resultado": RESULTADO_FALLO,
            "actor": str(token.get("sub", "anonimo")),
            "permisos_requeridos": ",".join(sorted(p.value for p in requeridos)),
            "modo": modo,
        },
    )


def require_permission(
    *permisos: Permiso, estricto: bool = False
) -> Callable[..., Awaitable[dict]]:
    """Factory de dependencia RBAC deny-by-default (AP-0053).

    Exige que el actor posea AL MENOS UNO de los permisos indicados (modo "any";
    para exigir varios, encadena dependencias). El enforcement se rige por
    Settings.authz_enforcement_mode salvo que estricto=True (guardias de
    administracion, que siempre fuerzan). En modo "audit" registra la denegacion y
    deja pasar (canary); en "off" deja pasar en silencio.
    """
    requeridos: frozenset[Permiso] = frozenset(permisos)

    async def _dep(token: TokenDep, settings: SettingsDep) -> dict:
        if _tiene_alguno(token, requeridos):
            return token
        modo: str = MODO_ENFORCE if estricto else settings.authz_enforcement_mode
        if modo in (MODO_ENFORCE, MODO_AUDIT):
            _auditar_denegacion(token, requeridos, modo)
        if modo == MODO_ENFORCE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permiso denegado: no autorizado para este recurso",
            )
        return token

    return _dep


def _exigir_estricto(token: dict, permiso: Permiso, mensaje: str) -> dict:
    """Verificacion dura (siempre 403 si falta), para los guardias de administracion
    ya en verde: no dependen del modo de enforcement."""
    if _tiene_alguno(token, frozenset({permiso})):
        return token
    _auditar_denegacion(token, frozenset({permiso}), MODO_ENFORCE)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=mensaje)


def require_admin_usuarios(token: TokenDep) -> dict:
    """Permiso USUARIOS_GESTIONAR_ESTADO (administrator o webmaster). Panel de
    Control para habilitar o deshabilitar cuentas (AP-0001)."""
    return _exigir_estricto(
        token,
        Permiso.USUARIOS_GESTIONAR_ESTADO,
        "Permiso denegado: USUARIOS_GESTIONAR_ESTADO requerido",
    )


def require_gestion_comisionistas(token: TokenDep) -> dict:
    """Guardia de la accion reutilizada en pantallas de asesor: deshabilitar la
    cuenta de un comisionista. El alcance exacto lo valida el caso de uso."""
    return _exigir_estricto(
        token,
        Permiso.COMISIONISTAS_GESTIONAR_ESTADO,
        "Permiso denegado: USUARIOS_GESTIONAR_ESTADO requerido",
    )


def require_admin_catalogos(token: TokenDep) -> dict:
    """Permiso ADMIN_CATALOGOS_GESTIONAR (rol administrator). Guardia de los
    endpoints administrativos del Panel de Control (CRUD de catalogos maestros)."""
    return _exigir_estricto(
        token,
        Permiso.ADMIN_CATALOGOS_GESTIONAR,
        "Permiso denegado: ADMIN_CATALOGOS_GESTIONAR requerido",
    )
