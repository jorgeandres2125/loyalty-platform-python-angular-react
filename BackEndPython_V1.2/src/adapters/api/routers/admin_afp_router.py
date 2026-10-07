from __future__ import annotations

from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.api.schemas.admin.afp.afp_form_request import AfpFormRequest
from src.adapters.api.schemas.admin.afp.afp_form_response import AfpFormResponse
from src.adapters.api.schemas.admin.afp.afp_list_item import AfpListItem
from src.adapters.api.schemas.admin.afp.afp_list_response import AfpListResponse
from src.application.dto.afp_form_dto import AfpFormDTO
from src.application.dto.afp_list_dto import AfpListDTO
from src.application.use_cases.gestionar_afp_use_case import GestionarAfpUseCase
from src.domain.entities.afp_entity import AfpEntity
from src.infrastructure.config.dependencies import get_admin_afp_uc
from src.infrastructure.config.permission_dependencies import require_admin_catalogos

router: APIRouter = APIRouter(dependencies=[Depends(require_admin_catalogos)])

_PAGE_SIZE_MAX: Final[int] = 100


@router.get(
    "",
    response_model=AfpListResponse,
    summary="Lista paginada de AFP (Panel de Control)",
)
async def listar_afp(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    nombre: Annotated[str | None, Query(max_length=200)] = None,
    uc: GestionarAfpUseCase = Depends(get_admin_afp_uc),
) -> AfpListResponse:
    result: AfpListDTO = await uc.listar_async(
        page=page,
        page_size=page_size,
        nombre=nombre,
    )
    items: list[AfpListItem] = [
        AfpListItem(tid=item.tid, nombre=item.nombre, nit=item.nit)
        for item in result.items
    ]
    return AfpListResponse(
        items=items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.get(
    "/{tid}",
    response_model=AfpFormResponse,
    summary="Obtener una AFP por tid",
)
async def obtener_afp(
    tid: int,
    uc: GestionarAfpUseCase = Depends(get_admin_afp_uc),
) -> AfpFormResponse:
    entity: AfpEntity | None = await uc.obtener_async(tid)
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AFP no encontrada"
        )
    return _to_response(entity)


@router.post(
    "",
    response_model=AfpFormResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva AFP",
)
async def crear_afp(
    body: AfpFormRequest,
    uc: GestionarAfpUseCase = Depends(get_admin_afp_uc),
) -> AfpFormResponse:
    dto: AfpFormDTO = AfpFormDTO(nombre=body.nombre, nit=body.nit)
    try:
        entity: AfpEntity = await uc.crear_async(dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return _to_response(entity)


@router.put(
    "/{tid}",
    response_model=AfpFormResponse,
    summary="Actualizar una AFP",
)
async def actualizar_afp(
    tid: int,
    body: AfpFormRequest,
    uc: GestionarAfpUseCase = Depends(get_admin_afp_uc),
) -> AfpFormResponse:
    dto: AfpFormDTO = AfpFormDTO(nombre=body.nombre, nit=body.nit)
    try:
        entity: AfpEntity | None = await uc.actualizar_async(tid, dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AFP no encontrada"
        )
    return _to_response(entity)


@router.delete(
    "/{tid}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar una AFP (hard delete con guardia de FK)",
)
async def eliminar_afp(
    tid: int,
    uc: GestionarAfpUseCase = Depends(get_admin_afp_uc),
) -> dict[str, bool]:
    try:
        eliminado: bool = await uc.eliminar_async(tid)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AFP no encontrada"
        )
    return {"ok": True}


def _to_response(entity: AfpEntity) -> AfpFormResponse:
    return AfpFormResponse(tid=entity.tid, nombre=entity.nombre, nit=entity.nit)
