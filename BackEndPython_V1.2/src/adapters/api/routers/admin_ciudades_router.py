from __future__ import annotations

from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.api.schemas.admin.ciudades.ciudad_form_request import (
    CiudadFormRequest,
)
from src.adapters.api.schemas.admin.ciudades.ciudad_form_response import (
    CiudadFormResponse,
)
from src.adapters.api.schemas.admin.ciudades.ciudad_list_item import CiudadListItem
from src.adapters.api.schemas.admin.ciudades.ciudad_list_response import (
    CiudadListResponse,
)
from src.application.dto.ciudad_form_dto import CiudadFormDTO
from src.application.dto.ciudad_list_dto import CiudadListDTO
from src.application.use_cases.gestionar_ciudades_use_case import (
    GestionarCiudadesUseCase,
)
from src.domain.entities.ciudad_entity import CiudadEntity
from src.infrastructure.config.dependencies import get_admin_ciudades_uc
from src.infrastructure.config.permission_dependencies import require_admin_catalogos

router: APIRouter = APIRouter(dependencies=[Depends(require_admin_catalogos)])

_PAGE_SIZE_MAX: Final[int] = 100


@router.get("", response_model=CiudadListResponse, summary="Lista paginada de ciudades")
async def listar_ciudades(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    nombre: Annotated[str | None, Query(max_length=50)] = None,
    did: Annotated[int | None, Query(description="Filtrar por departamento")] = None,
    uc: GestionarCiudadesUseCase = Depends(get_admin_ciudades_uc),
) -> CiudadListResponse:
    result: CiudadListDTO = await uc.listar_async(
        page=page, page_size=page_size, nombre=nombre, did=did
    )
    items: list[CiudadListItem] = [
        CiudadListItem(cid=i.cid, did=i.did, ciudad=i.ciudad) for i in result.items
    ]
    return CiudadListResponse(
        items=items, total=result.total, page=result.page, page_size=result.page_size
    )


@router.get("/{cid}", response_model=CiudadFormResponse, summary="Obtener ciudad por cid")
async def obtener_ciudad(
    cid: int, uc: GestionarCiudadesUseCase = Depends(get_admin_ciudades_uc)
) -> CiudadFormResponse:
    entity: CiudadEntity | None = await uc.obtener_async(cid)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ciudad no encontrada")
    return _to_response(entity)


@router.post(
    "",
    response_model=CiudadFormResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva ciudad",
)
async def crear_ciudad(
    body: CiudadFormRequest,
    uc: GestionarCiudadesUseCase = Depends(get_admin_ciudades_uc),
) -> CiudadFormResponse:
    dto: CiudadFormDTO = CiudadFormDTO(ciudad=body.ciudad, did=body.did)
    try:
        entity: CiudadEntity = await uc.crear_async(dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _to_response(entity)


@router.put("/{cid}", response_model=CiudadFormResponse, summary="Actualizar una ciudad")
async def actualizar_ciudad(
    cid: int,
    body: CiudadFormRequest,
    uc: GestionarCiudadesUseCase = Depends(get_admin_ciudades_uc),
) -> CiudadFormResponse:
    dto: CiudadFormDTO = CiudadFormDTO(ciudad=body.ciudad, did=body.did)
    try:
        entity: CiudadEntity | None = await uc.actualizar_async(cid, dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ciudad no encontrada")
    return _to_response(entity)


@router.delete("/{cid}", status_code=status.HTTP_200_OK, summary="Eliminar una ciudad")
async def eliminar_ciudad(
    cid: int, uc: GestionarCiudadesUseCase = Depends(get_admin_ciudades_uc)
) -> dict[str, bool]:
    try:
        eliminado: bool = await uc.eliminar_async(cid)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if not eliminado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ciudad no encontrada")
    return {"ok": True}


def _to_response(entity: CiudadEntity) -> CiudadFormResponse:
    return CiudadFormResponse(cid=entity.cid, did=entity.did, ciudad=entity.ciudad)
