from __future__ import annotations

from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.api.auditoria_critica import auditar_operacion_critica
from src.adapters.api.schemas.canal.canal_form_request import CanalFormRequest
from src.adapters.api.schemas.canal.canal_form_response import CanalFormResponse
from src.adapters.api.schemas.canal.canal_list_item import CanalListItem
from src.adapters.api.schemas.canal.canal_list_response import CanalListResponse
from src.adapters.api.schemas.canal_activa_schema import CanalActivaItem
from src.application.dto.canal_form_dto import CanalFormDTO
from src.application.dto.canal_list_dto import CanalListDTO
from src.application.services.servicio_auditoria import ServicioAuditoria
from src.application.use_cases.gestionar_canales_use_case import GestionarCanalesUseCase
from src.domain.entities.canal_entity import CanalEntity
from src.domain.value_objects.permiso import Permiso
from src.infrastructure.config.dependencies import (
    TokenDep,
    get_canales_uc,
    get_servicio_auditoria,
)
from src.infrastructure.config.permission_dependencies import (
    actor_desde_token,
    require_permission,
)

router: APIRouter = APIRouter()

_PAGE_SIZE_MAX: Final[int] = 100


@router.get(
    "",
    response_model=CanalListResponse,
    summary="Lista paginada de canales",
)
async def listar_canales(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    nombre: Annotated[str | None, Query(max_length=120)] = None,
    ind_activo: Annotated[bool | None, Query()] = None,
    uc: GestionarCanalesUseCase = Depends(get_canales_uc),
) -> CanalListResponse:
    result: CanalListDTO = await uc.listar_async(
        page=page,
        page_size=page_size,
        nombre=nombre,
        ind_activo=ind_activo,
    )
    items: list[CanalListItem] = [
        CanalListItem(
            cod_canales=item.cod_canales,
            nom_canales=item.nom_canales,
            cpid=item.cpid,
            cspid=item.cspid,
            ind_activo=item.ind_activo,
            id_canales=item.id_canales,
        )
        for item in result.items
    ]
    return CanalListResponse(
        items=items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.get(
    "/activas",
    response_model=list[CanalActivaItem],
    summary="Lista compacta de canales activos (para dropdowns)",
)
async def listar_canales_activas(
    uc: GestionarCanalesUseCase = Depends(get_canales_uc),
) -> list[CanalActivaItem]:
    entities: list[CanalEntity] = await uc.listar_activas_async()
    return [
        CanalActivaItem(
            cod_canales=entity.cod_canales or 0,
            nom_canales=entity.nom_canales,
        )
        for entity in entities
        if entity.cod_canales is not None
    ]


@router.get(
    "/{cod_canales}",
    response_model=CanalFormResponse,
    summary="Obtener canal por código",
)
async def obtener_canal(
    cod_canales: int,
    uc: GestionarCanalesUseCase = Depends(get_canales_uc),
) -> CanalFormResponse:
    entity: CanalEntity | None = await uc.obtener_async(cod_canales)
    if entity is None or entity.cod_canales is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canal no encontrado")
    return _to_response(entity)


@router.post(
    "",
    response_model=CanalFormResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear canal",
    dependencies=[Depends(require_permission(Permiso.CATALOGOS_REFERENCIA_GESTIONAR))],
)
async def crear_canal(
    token: TokenDep,
    body: CanalFormRequest,
    uc: GestionarCanalesUseCase = Depends(get_canales_uc),
    auditoria: ServicioAuditoria = Depends(get_servicio_auditoria),
) -> CanalFormResponse:
    dto: CanalFormDTO = _to_dto(body)
    try:
        entity: CanalEntity = await uc.crear_async(dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    actor_uid, _roles = actor_desde_token(token)
    await auditar_operacion_critica(
        auditoria, actor_uid, "crear_canal", "canal", str(entity.cod_canales)
    )
    return _to_response(entity)


@router.put(
    "/{cod_canales}",
    response_model=CanalFormResponse,
    summary="Actualizar canal",
    dependencies=[Depends(require_permission(Permiso.CATALOGOS_REFERENCIA_GESTIONAR))],
)
async def actualizar_canal(
    token: TokenDep,
    cod_canales: int,
    body: CanalFormRequest,
    uc: GestionarCanalesUseCase = Depends(get_canales_uc),
    auditoria: ServicioAuditoria = Depends(get_servicio_auditoria),
) -> CanalFormResponse:
    dto: CanalFormDTO = _to_dto(body)
    try:
        entity: CanalEntity | None = await uc.actualizar_async(cod_canales, dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if entity is None or entity.cod_canales is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canal no encontrado")
    actor_uid, _roles = actor_desde_token(token)
    await auditar_operacion_critica(
        auditoria, actor_uid, "actualizar_canal", "canal", str(entity.cod_canales)
    )
    return _to_response(entity)


def _to_dto(body: CanalFormRequest) -> CanalFormDTO:
    return CanalFormDTO(
        nom_canales=body.nom_canales,
        cpid=body.cpid,
        cspid=body.cspid,
        ind_activo=body.ind_activo,
        oficinas_ids=list(body.oficinas_ids),
    )


def _to_response(entity: CanalEntity) -> CanalFormResponse:
    return CanalFormResponse(
        cod_canales=entity.cod_canales or 0,
        nom_canales=entity.nom_canales,
        cpid=entity.cpid,
        cspid=entity.cspid,
        ind_activo=bool(entity.ind_activo),
        id_canales=entity.id_canales,
        oficinas_ids=list(entity.oficinas_ids),
    )
