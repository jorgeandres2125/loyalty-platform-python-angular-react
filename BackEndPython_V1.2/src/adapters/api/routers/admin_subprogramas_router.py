from __future__ import annotations

from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.api.schemas.admin.subprogramas.admin_subprograma_form_request import (
    AdminSubprogramaFormRequest,
)
from src.adapters.api.schemas.admin.subprogramas.admin_subprograma_form_response import (
    AdminSubprogramaFormResponse,
)
from src.adapters.api.schemas.admin.subprogramas.admin_subprograma_list_item import (
    AdminSubprogramaListItem,
)
from src.adapters.api.schemas.admin.subprogramas.admin_subprograma_list_response import (
    AdminSubprogramaListResponse,
)
from src.application.dto.admin_subprograma_form_dto import AdminSubprogramaFormDTO
from src.application.dto.admin_subprograma_list_dto import AdminSubprogramaListDTO
from src.application.use_cases.gestionar_admin_subprogramas_use_case import (
    GestionarAdminSubprogramasUseCase,
)
from src.domain.entities.comisionista_subprograma_entity import (
    ComisionistaSubprogramaEntity,
)
from src.infrastructure.config.dependencies import get_admin_subprogramas_uc
from src.infrastructure.config.permission_dependencies import require_admin_catalogos

router: APIRouter = APIRouter(dependencies=[Depends(require_admin_catalogos)])

_PAGE_SIZE_MAX: Final[int] = 100


@router.get(
    "",
    response_model=AdminSubprogramaListResponse,
    summary="Lista paginada de sub-programas",
)
async def listar_subprogramas(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    nombre: Annotated[str | None, Query(max_length=45)] = None,
    cpid: Annotated[int | None, Query(description="Filtrar por programa")] = None,
    uc: GestionarAdminSubprogramasUseCase = Depends(get_admin_subprogramas_uc),
) -> AdminSubprogramaListResponse:
    result: AdminSubprogramaListDTO = await uc.listar_async(
        page=page, page_size=page_size, nombre=nombre, cpid=cpid
    )
    items: list[AdminSubprogramaListItem] = [
        AdminSubprogramaListItem(
            cspid=i.cspid, cspid_nombre=i.cspid_nombre, cpid=i.cpid
        )
        for i in result.items
    ]
    return AdminSubprogramaListResponse(
        items=items, total=result.total, page=result.page, page_size=result.page_size
    )


@router.get(
    "/{cspid}",
    response_model=AdminSubprogramaFormResponse,
    summary="Obtener sub-programa por cspid",
)
async def obtener_subprograma(
    cspid: int,
    uc: GestionarAdminSubprogramasUseCase = Depends(get_admin_subprogramas_uc),
) -> AdminSubprogramaFormResponse:
    entity: ComisionistaSubprogramaEntity | None = await uc.obtener_async(cspid)
    if entity is None or entity.cspid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sub-programa no encontrado"
        )
    return _to_response(entity)


@router.post(
    "",
    response_model=AdminSubprogramaFormResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo sub-programa",
)
async def crear_subprograma(
    body: AdminSubprogramaFormRequest,
    uc: GestionarAdminSubprogramasUseCase = Depends(get_admin_subprogramas_uc),
) -> AdminSubprogramaFormResponse:
    dto: AdminSubprogramaFormDTO = AdminSubprogramaFormDTO(
        cspid_nombre=body.cspid_nombre, cpid=body.cpid
    )
    try:
        entity: ComisionistaSubprogramaEntity = await uc.crear_async(dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return _to_response(entity)


@router.put(
    "/{cspid}",
    response_model=AdminSubprogramaFormResponse,
    summary="Actualizar un sub-programa",
)
async def actualizar_subprograma(
    cspid: int,
    body: AdminSubprogramaFormRequest,
    uc: GestionarAdminSubprogramasUseCase = Depends(get_admin_subprogramas_uc),
) -> AdminSubprogramaFormResponse:
    dto: AdminSubprogramaFormDTO = AdminSubprogramaFormDTO(
        cspid_nombre=body.cspid_nombre, cpid=body.cpid
    )
    try:
        entity: ComisionistaSubprogramaEntity | None = await uc.actualizar_async(cspid, dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    if entity is None or entity.cspid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sub-programa no encontrado"
        )
    return _to_response(entity)


@router.delete(
    "/{cspid}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar un sub-programa",
)
async def eliminar_subprograma(
    cspid: int,
    uc: GestionarAdminSubprogramasUseCase = Depends(get_admin_subprogramas_uc),
) -> dict[str, bool]:
    try:
        eliminado: bool = await uc.eliminar_async(cspid)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sub-programa no encontrado"
        )
    return {"ok": True}


def _to_response(
    entity: ComisionistaSubprogramaEntity,
) -> AdminSubprogramaFormResponse:
    return AdminSubprogramaFormResponse(
        cspid=entity.cspid or 0, cspid_nombre=entity.cspid_nombre, cpid=entity.cpid
    )
