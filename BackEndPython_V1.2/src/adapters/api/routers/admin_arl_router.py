from __future__ import annotations

from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.api.schemas.admin.arl.arl_form_request import ArlFormRequest
from src.adapters.api.schemas.admin.arl.arl_form_response import ArlFormResponse
from src.adapters.api.schemas.admin.arl.arl_list_item import ArlListItem
from src.adapters.api.schemas.admin.arl.arl_list_response import ArlListResponse
from src.application.dto.arl_form_dto import ArlFormDTO
from src.application.dto.arl_list_dto import ArlListDTO
from src.application.use_cases.gestionar_arl_use_case import GestionarArlUseCase
from src.domain.entities.arl_entity import ArlEntity
from src.infrastructure.config.dependencies import get_admin_arl_uc
from src.infrastructure.config.permission_dependencies import require_admin_catalogos

router: APIRouter = APIRouter(dependencies=[Depends(require_admin_catalogos)])

_PAGE_SIZE_MAX: Final[int] = 100


@router.get("", response_model=ArlListResponse, summary="Lista paginada de ARL")
async def listar_arl(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    nombre: Annotated[str | None, Query(max_length=200)] = None,
    uc: GestionarArlUseCase = Depends(get_admin_arl_uc),
) -> ArlListResponse:
    result: ArlListDTO = await uc.listar_async(page=page, page_size=page_size, nombre=nombre)
    items: list[ArlListItem] = [
        ArlListItem(tid=item.tid, nombre=item.nombre, nit=item.nit) for item in result.items
    ]
    return ArlListResponse(items=items, total=result.total, page=result.page, page_size=result.page_size)


@router.get("/{tid}", response_model=ArlFormResponse, summary="Obtener una ARL por tid")
async def obtener_arl(
    tid: int, uc: GestionarArlUseCase = Depends(get_admin_arl_uc)
) -> ArlFormResponse:
    entity: ArlEntity | None = await uc.obtener_async(tid)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ARL no encontrada")
    return _to_response(entity)


@router.post(
    "",
    response_model=ArlFormResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva ARL",
)
async def crear_arl(
    body: ArlFormRequest, uc: GestionarArlUseCase = Depends(get_admin_arl_uc)
) -> ArlFormResponse:
    dto: ArlFormDTO = ArlFormDTO(nombre=body.nombre, nit=body.nit)
    try:
        entity: ArlEntity = await uc.crear_async(dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _to_response(entity)


@router.put("/{tid}", response_model=ArlFormResponse, summary="Actualizar una ARL")
async def actualizar_arl(
    tid: int,
    body: ArlFormRequest,
    uc: GestionarArlUseCase = Depends(get_admin_arl_uc),
) -> ArlFormResponse:
    dto: ArlFormDTO = ArlFormDTO(nombre=body.nombre, nit=body.nit)
    try:
        entity: ArlEntity | None = await uc.actualizar_async(tid, dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ARL no encontrada")
    return _to_response(entity)


@router.delete("/{tid}", status_code=status.HTTP_200_OK, summary="Eliminar una ARL")
async def eliminar_arl(
    tid: int, uc: GestionarArlUseCase = Depends(get_admin_arl_uc)
) -> dict[str, bool]:
    try:
        eliminado: bool = await uc.eliminar_async(tid)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if not eliminado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ARL no encontrada")
    return {"ok": True}


def _to_response(entity: ArlEntity) -> ArlFormResponse:
    return ArlFormResponse(tid=entity.tid, nombre=entity.nombre, nit=entity.nit)
