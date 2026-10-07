from __future__ import annotations

from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.api.auditoria_critica import auditar_operacion_critica
from src.adapters.api.schemas.oficina.oficina_form_request import OficinaFormRequest
from src.adapters.api.schemas.oficina.oficina_form_response import OficinaFormResponse
from src.adapters.api.schemas.oficina.oficina_list_item import OficinaListItem
from src.adapters.api.schemas.oficina.oficina_list_response import OficinaListResponse
from src.adapters.api.schemas.oficina_activa_schema import OficinaActivaItem
from src.application.dto.oficina_form_dto import OficinaFormDTO
from src.application.dto.oficina_list_dto import OficinaListDTO
from src.application.services.servicio_auditoria import ServicioAuditoria
from src.application.use_cases.gestionar_oficinas_use_case import GestionarOficinasUseCase
from src.domain.entities.oficina_entity import OficinaEntity
from src.domain.value_objects.permiso import Permiso
from src.infrastructure.config.dependencies import (
    TokenDep,
    get_oficinas_uc,
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
    response_model=OficinaListResponse,
    summary="Lista paginada de oficinas",
)
async def listar_oficinas(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    nombre: Annotated[str | None, Query(max_length=120)] = None,
    marca: Annotated[str | None, Query(max_length=45)] = None,
    regional: Annotated[str | None, Query(max_length=45)] = None,
    ind_activo: Annotated[bool | None, Query()] = None,
    uc: GestionarOficinasUseCase = Depends(get_oficinas_uc),
) -> OficinaListResponse:
    result: OficinaListDTO = await uc.listar_async(
        page=page,
        page_size=page_size,
        nombre=nombre,
        marca=marca,
        regional=regional,
        ind_activo=ind_activo,
    )
    items: list[OficinaListItem] = [
        OficinaListItem(
            cod_oficinas=item.cod_oficinas,
            id_oficinas=item.id_oficinas,
            nom_oficinas=item.nom_oficinas,
            marca=item.marca,
            regional=item.regional,
            cpid=item.cpid,
            ind_activo=item.ind_activo,
            ciudad_nombre=item.ciudad_nombre,
            did=item.did,
            departamento_nombre=item.departamento_nombre,
        )
        for item in result.items
    ]
    return OficinaListResponse(
        items=items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.get(
    "/activas",
    response_model=list[OficinaActivaItem],
    summary="Lista compacta de oficinas activas (para dropdowns)",
)
async def listar_oficinas_activas(
    uc: GestionarOficinasUseCase = Depends(get_oficinas_uc),
) -> list[OficinaActivaItem]:
    entities: list[OficinaEntity] = await uc.listar_activas_async()
    return [
        OficinaActivaItem(
            cod_oficinas=entity.cod_oficinas or 0,
            nom_oficinas=entity.nom_oficinas,
        )
        for entity in entities
        if entity.cod_oficinas is not None
    ]


@router.get(
    "/{cod_oficinas}",
    response_model=OficinaFormResponse,
    summary="Obtener oficina por código",
)
async def obtener_oficina(
    cod_oficinas: int,
    uc: GestionarOficinasUseCase = Depends(get_oficinas_uc),
) -> OficinaFormResponse:
    entity: OficinaEntity | None = await uc.obtener_async(cod_oficinas)
    if entity is None or entity.cod_oficinas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oficina no encontrada")
    return _to_response(entity)


@router.post(
    "",
    response_model=OficinaFormResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear oficina",
    dependencies=[Depends(require_permission(Permiso.CATALOGOS_REFERENCIA_GESTIONAR))],
)
async def crear_oficina(
    token: TokenDep,
    body: OficinaFormRequest,
    uc: GestionarOficinasUseCase = Depends(get_oficinas_uc),
    auditoria: ServicioAuditoria = Depends(get_servicio_auditoria),
) -> OficinaFormResponse:
    dto: OficinaFormDTO = _to_dto(body)
    try:
        entity: OficinaEntity = await uc.crear_async(dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    actor_uid, _roles = actor_desde_token(token)
    await auditar_operacion_critica(
        auditoria, actor_uid, "crear_oficina", "oficina", str(entity.cod_oficinas)
    )
    return _to_response(entity)


@router.put(
    "/{cod_oficinas}",
    response_model=OficinaFormResponse,
    summary="Actualizar oficina",
    dependencies=[Depends(require_permission(Permiso.CATALOGOS_REFERENCIA_GESTIONAR))],
)
async def actualizar_oficina(
    token: TokenDep,
    cod_oficinas: int,
    body: OficinaFormRequest,
    uc: GestionarOficinasUseCase = Depends(get_oficinas_uc),
    auditoria: ServicioAuditoria = Depends(get_servicio_auditoria),
) -> OficinaFormResponse:
    dto: OficinaFormDTO = _to_dto(body)
    try:
        entity: OficinaEntity | None = await uc.actualizar_async(cod_oficinas, dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if entity is None or entity.cod_oficinas is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oficina no encontrada")
    actor_uid, _roles = actor_desde_token(token)
    await auditar_operacion_critica(
        auditoria, actor_uid, "actualizar_oficina", "oficina", str(entity.cod_oficinas)
    )
    return _to_response(entity)


def _to_dto(body: OficinaFormRequest) -> OficinaFormDTO:
    return OficinaFormDTO(
        nom_oficinas=body.nom_oficinas,
        marca=body.marca,
        regional=body.regional,
        cpid=body.cpid,
        ind_activo=body.ind_activo,
        canales_ids=list(body.canales_ids),
    )


def _to_response(entity: OficinaEntity) -> OficinaFormResponse:
    return OficinaFormResponse(
        cod_oficinas=entity.cod_oficinas or 0,
        id_oficinas=entity.id_oficinas,
        nom_oficinas=entity.nom_oficinas,
        marca=entity.marca,
        regional=entity.regional,
        cpid=entity.cpid,
        ind_activo=bool(entity.ind_activo),
        ciudad_nombre=entity.ciudad_nombre,
        did=entity.did,
        departamento_nombre=entity.departamento_nombre,
        canales_ids=list(entity.canales_ids),
    )
