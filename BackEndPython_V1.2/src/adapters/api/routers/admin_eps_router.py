from __future__ import annotations

from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.api.schemas.admin.eps.eps_form_request import EpsFormRequest
from src.adapters.api.schemas.admin.eps.eps_form_response import EpsFormResponse
from src.adapters.api.schemas.admin.eps.eps_list_item import EpsListItem
from src.adapters.api.schemas.admin.eps.eps_list_response import EpsListResponse
from src.application.dto.eps_form_dto import EpsFormDTO
from src.application.dto.eps_list_dto import EpsListDTO
from src.application.use_cases.gestionar_eps_use_case import GestionarEpsUseCase
from src.domain.entities.eps_entity import EpsEntity
from src.infrastructure.config.dependencies import get_admin_eps_uc
from src.infrastructure.config.permission_dependencies import require_admin_catalogos

router: APIRouter = APIRouter(dependencies=[Depends(require_admin_catalogos)])

_PAGE_SIZE_MAX: Final[int] = 100


@router.get("", response_model=EpsListResponse, summary="Lista paginada de EPS")
async def listar_eps(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    nombre: Annotated[str | None, Query(max_length=200)] = None,
    uc: GestionarEpsUseCase = Depends(get_admin_eps_uc),
) -> EpsListResponse:
    result: EpsListDTO = await uc.listar_async(page=page, page_size=page_size, nombre=nombre)
    items: list[EpsListItem] = [
        EpsListItem(tid=i.tid, nombre=i.nombre, nit=i.nit) for i in result.items
    ]
    return EpsListResponse(items=items, total=result.total, page=result.page, page_size=result.page_size)


@router.get("/{tid}", response_model=EpsFormResponse, summary="Obtener una EPS por tid")
async def obtener_eps(tid: int, uc: GestionarEpsUseCase = Depends(get_admin_eps_uc)) -> EpsFormResponse:
    entity: EpsEntity | None = await uc.obtener_async(tid)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="EPS no encontrada")
    return _to_response(entity)


@router.post("", response_model=EpsFormResponse, status_code=status.HTTP_201_CREATED, summary="Crear una nueva EPS")
async def crear_eps(body: EpsFormRequest, uc: GestionarEpsUseCase = Depends(get_admin_eps_uc)) -> EpsFormResponse:
    dto: EpsFormDTO = EpsFormDTO(nombre=body.nombre, nit=body.nit)
    try:
        entity: EpsEntity = await uc.crear_async(dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _to_response(entity)


@router.put("/{tid}", response_model=EpsFormResponse, summary="Actualizar una EPS")
async def actualizar_eps(
    tid: int, body: EpsFormRequest, uc: GestionarEpsUseCase = Depends(get_admin_eps_uc)
) -> EpsFormResponse:
    dto: EpsFormDTO = EpsFormDTO(nombre=body.nombre, nit=body.nit)
    try:
        entity: EpsEntity | None = await uc.actualizar_async(tid, dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="EPS no encontrada")
    return _to_response(entity)


@router.delete("/{tid}", status_code=status.HTTP_200_OK, summary="Eliminar una EPS")
async def eliminar_eps(tid: int, uc: GestionarEpsUseCase = Depends(get_admin_eps_uc)) -> dict[str, bool]:
    try:
        eliminado: bool = await uc.eliminar_async(tid)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if not eliminado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="EPS no encontrada")
    return {"ok": True}


def _to_response(entity: EpsEntity) -> EpsFormResponse:
    return EpsFormResponse(tid=entity.tid, nombre=entity.nombre, nit=entity.nit)
