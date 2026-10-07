from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.api.schemas.auditoria.historial_auditoria_response import (
    HistorialAuditoriaResponse,
)
from src.adapters.api.schemas.auditoria.registro_auditoria_response import (
    RegistroAuditoriaResponse,
)
from src.application.use_cases.consultar_mi_historial_use_case import (
    ConsultarMiHistorialUseCase,
)
from src.domain.value_objects.filtro_auditoria import FiltroAuditoria
from src.domain.value_objects.pagina_auditoria import PaginaAuditoria
from src.infrastructure.config.dependencies import (
    get_consultar_mi_historial_uc,
    require_token,
)
from src.shared.constants.auditoria import (
    HISTORIAL_PAGE_SIZE_DEFECTO,
    HISTORIAL_PAGE_SIZE_MAX,
    ROLES_HISTORIAL_PERMITIDOS,
)

# AP-0028: historial de acciones del propio usuario. Filtra SIEMPRE por el usuario del token
# (nunca acepta user_id por parametro). Cualquier usuario autenticado ve solo lo suyo.
router: APIRouter = APIRouter()


def _uid_de_token(token: dict[str, object]) -> int:
    try:
        return int(str(token.get("sub", 0)))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido"
        ) from exc


def _roles_de_token(token: dict[str, object]) -> set[str]:
    crudos: object = token.get("roles") or []
    if not isinstance(crudos, list):
        return set()
    return {str(rol) for rol in crudos}


def _exigir_rol_historial(token: dict[str, object]) -> None:
    # AP-0028: usuarios autorizados = quienes tienen un rol operativo del portal.
    if ROLES_HISTORIAL_PERMITIDOS.isdisjoint(_roles_de_token(token)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes un rol autorizado para consultar el historial de auditoria",
        )


@router.get(
    "/historial",
    response_model=HistorialAuditoriaResponse,
    summary="Consultar mi historial de acciones (AP-0028)",
)
async def mi_historial(
    token: dict[str, object] = Depends(require_token),
    uc: ConsultarMiHistorialUseCase = Depends(get_consultar_mi_historial_uc),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(
        default=HISTORIAL_PAGE_SIZE_DEFECTO, ge=1, le=HISTORIAL_PAGE_SIZE_MAX
    ),
    accion: str | None = Query(default=None, max_length=80),
    desde: str | None = Query(default=None, description="Instante ISO 8601 inicial"),
    hasta: str | None = Query(default=None, description="Instante ISO 8601 final"),
) -> HistorialAuditoriaResponse:
    _exigir_rol_historial(token)
    user_id: int = _uid_de_token(token)
    filtro: FiltroAuditoria = FiltroAuditoria(
        page=page, page_size=page_size, accion=accion, desde_iso=desde, hasta_iso=hasta
    )
    pagina: PaginaAuditoria = await uc.ejecutar_async(user_id, filtro)
    return HistorialAuditoriaResponse(
        items=[
            RegistroAuditoriaResponse(
                id=reg.id,
                accion=reg.accion,
                entidad=reg.entidad,
                entidad_id=reg.entidad_id,
                detalle=reg.detalle,
                ip_origen=reg.ip_origen,
                resultado=reg.resultado,
                creado_en=reg.creado_iso,
            )
            for reg in pagina.items
        ],
        page=pagina.page,
        page_size=pagina.page_size,
        total=pagina.total,
    )
