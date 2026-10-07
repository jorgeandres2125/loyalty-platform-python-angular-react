from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Depends, HTTPException, Request

from src.application.services.authorization_service import AuthorizationService
from src.domain.value_objects.accion_recurso import AccionRecurso
from src.domain.value_objects.decision_acceso import DecisionAcceso
from src.domain.value_objects.resource_type import ResourceType
from src.infrastructure.config.dependencies import TokenDep, get_authorization_service
from src.infrastructure.config.permission_dependencies import actor_desde_token


def aplicar_decision(decision: DecisionAcceso) -> None:
    """AP-0055: traduce una DecisionAcceso denegada al error HTTP correspondiente
    (403 o 404 segun la politica). No hace nada si la decision permite el acceso."""
    if not decision.permitido:
        raise HTTPException(status_code=decision.status, detail=decision.mensaje)


async def autorizar_objeto(
    authz: AuthorizationService,
    token: dict[str, object],
    tipo: ResourceType,
    accion: AccionRecurso,
    resource_id: str | None,
) -> None:
    """AP-0055: evalua la politica de acceso a un objeto y deniega (403 o 404) si el
    actor no esta autorizado. Para endpoints que reciben el id del recurso en el
    cuerpo (el id de ruta lo cubre require_object_access)."""
    actor_uid, roles = actor_desde_token(token)
    decision: DecisionAcceso = await authz.autorizar(
        actor_uid, frozenset(roles), tipo, accion, resource_id
    )
    aplicar_decision(decision)


def require_object_access(
    tipo: ResourceType, accion: AccionRecurso, id_param: str
) -> Callable[..., Awaitable[dict[str, object]]]:
    """AP-0055: dependencia de autorizacion a nivel de objeto para endpoints que
    reciben el id del recurso en la RUTA. Extrae el id del path, evalua la politica
    via AuthorizationService y deniega (403 o 404) antes de tocar la logica."""

    async def _dep(
        request: Request,
        token: TokenDep,
        authz: AuthorizationService = Depends(get_authorization_service),
    ) -> dict[str, object]:
        resource_id: str | None = request.path_params.get(id_param)
        await autorizar_objeto(authz, token, tipo, accion, resource_id)
        return token

    return _dep