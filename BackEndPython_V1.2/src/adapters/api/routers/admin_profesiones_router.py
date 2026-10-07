from __future__ import annotations

from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.api.schemas.admin.profesiones.profesion_form_request import (
    ProfesionFormRequest,
)
from src.adapters.api.schemas.admin.profesiones.profesion_form_response import (
    ProfesionFormResponse,
)
from src.adapters.api.schemas.admin.profesiones.profesion_list_item import (
    ProfesionListItem,
)
from src.adapters.api.schemas.admin.profesiones.profesion_list_response import (
    ProfesionListResponse,
)
from src.application.dto.profesion_form_dto import ProfesionFormDTO
from src.application.dto.profesion_list_dto import ProfesionListDTO
from src.application.use_cases.gestionar_profesiones_use_case import (
    GestionarProfesionesUseCase,
)
from src.domain.entities.profesion_entity import ProfesionEntity
from src.infrastructure.config.dependencies import get_admin_profesiones_uc
from src.infrastructure.config.permission_dependencies import require_admin_catalogos

router: APIRouter = APIRouter(dependencies=[Depends(require_admin_catalogos)])

_PAGE_SIZE_MAX: Final[int] = 100


@router.get("", response_model=ProfesionListResponse, summary="Lista paginada de profesiones")
async def listar_profesiones(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    nombre: Annotated[str | None, Query(max_length=220)] = None,
    uc: GestionarProfesionesUseCase = Depends(get_admin_profesiones_uc),
) -> ProfesionListResponse:
    result: ProfesionListDTO = await uc.listar_async(page=page, page_size=page_size, nombre=nombre)
    items: list[ProfesionListItem] = [
        ProfesionListItem(tid=i.tid, nombre=i.nombre) for i in result.items
    ]
    return ProfesionListResponse(items=items, total=result.total, page=result.page, page_size=result.page_size)


@router.get("/{tid}", response_model=ProfesionFormResponse, summary="Obtener profesión por tid")
async def obtener_profesion(
    tid: int, uc: GestionarProfesionesUseCase = Depends(get_admin_profesiones_uc)
) -> ProfesionFormResponse:
    entity: ProfesionEntity | None = await uc.obtener_async(tid)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesión no encontrada")
    return _to_response(entity)


@router.post(
    "",
    response_model=ProfesionFormResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva profesión",
)
async def crear_profesion(
    body: ProfesionFormRequest,
    uc: GestionarProfesionesUseCase = Depends(get_admin_profesiones_uc),
) -> ProfesionFormResponse:
    dto: ProfesionFormDTO = ProfesionFormDTO(nombre=body.nombre)
    try:
        entity: ProfesionEntity = await uc.crear_async(dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _to_response(entity)


@router.put("/{tid}", response_model=ProfesionFormResponse, summary="Actualizar una profesión")
async def actualizar_profesion(
    tid: int,
    body: ProfesionFormRequest,
    uc: GestionarProfesionesUseCase = Depends(get_admin_profesiones_uc),
) -> ProfesionFormResponse:
    dto: ProfesionFormDTO = ProfesionFormDTO(nombre=body.nombre)
    try:
        entity: ProfesionEntity | None = await uc.actualizar_async(tid, dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesión no encontrada")
    return _to_response(entity)


@router.delete("/{tid}", status_code=status.HTTP_200_OK, summary="Eliminar una profesión")
async def eliminar_profesion(
    tid: int, uc: GestionarProfesionesUseCase = Depends(get_admin_profesiones_uc)
) -> dict[str, bool]:
    try:
        eliminado: bool = await uc.eliminar_async(tid)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if not eliminado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesión no encontrada")
    return {"ok": True}


def _to_response(entity: ProfesionEntity) -> ProfesionFormResponse:
    return ProfesionFormResponse(tid=entity.tid, nombre=entity.nombre)
