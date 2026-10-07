from __future__ import annotations

from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.api.schemas.admin.bancos.banco_form_request import BancoFormRequest
from src.adapters.api.schemas.admin.bancos.banco_form_response import BancoFormResponse
from src.adapters.api.schemas.admin.bancos.banco_list_item import BancoListItem
from src.adapters.api.schemas.admin.bancos.banco_list_response import BancoListResponse
from src.application.dto.banco_form_dto import BancoFormDTO
from src.application.dto.banco_list_dto import BancoListDTO
from src.application.use_cases.gestionar_bancos_use_case import GestionarBancosUseCase
from src.domain.entities.banco_entity import BancoEntity
from src.infrastructure.config.dependencies import get_admin_bancos_uc
from src.infrastructure.config.permission_dependencies import require_admin_catalogos

router: APIRouter = APIRouter(dependencies=[Depends(require_admin_catalogos)])

_PAGE_SIZE_MAX: Final[int] = 100


@router.get("", response_model=BancoListResponse, summary="Lista paginada de bancos")
async def listar_bancos(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    nombre: Annotated[str | None, Query(max_length=200)] = None,
    uc: GestionarBancosUseCase = Depends(get_admin_bancos_uc),
) -> BancoListResponse:
    result: BancoListDTO = await uc.listar_async(page=page, page_size=page_size, nombre=nombre)
    items: list[BancoListItem] = [
        BancoListItem(tid=i.tid, nombre=i.nombre, codigo=i.codigo) for i in result.items
    ]
    return BancoListResponse(items=items, total=result.total, page=result.page, page_size=result.page_size)


@router.get("/{tid}", response_model=BancoFormResponse, summary="Obtener un banco por tid")
async def obtener_banco(
    tid: int, uc: GestionarBancosUseCase = Depends(get_admin_bancos_uc)
) -> BancoFormResponse:
    entity: BancoEntity | None = await uc.obtener_async(tid)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banco no encontrado")
    return _to_response(entity)


@router.post(
    "",
    response_model=BancoFormResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo banco",
)
async def crear_banco(
    body: BancoFormRequest, uc: GestionarBancosUseCase = Depends(get_admin_bancos_uc)
) -> BancoFormResponse:
    dto: BancoFormDTO = BancoFormDTO(nombre=body.nombre, codigo=body.codigo)
    try:
        entity: BancoEntity = await uc.crear_async(dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _to_response(entity)


@router.put("/{tid}", response_model=BancoFormResponse, summary="Actualizar un banco")
async def actualizar_banco(
    tid: int,
    body: BancoFormRequest,
    uc: GestionarBancosUseCase = Depends(get_admin_bancos_uc),
) -> BancoFormResponse:
    dto: BancoFormDTO = BancoFormDTO(nombre=body.nombre, codigo=body.codigo)
    try:
        entity: BancoEntity | None = await uc.actualizar_async(tid, dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banco no encontrado")
    return _to_response(entity)


@router.delete("/{tid}", status_code=status.HTTP_200_OK, summary="Eliminar un banco")
async def eliminar_banco(
    tid: int, uc: GestionarBancosUseCase = Depends(get_admin_bancos_uc)
) -> dict[str, bool]:
    try:
        eliminado: bool = await uc.eliminar_async(tid)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if not eliminado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banco no encontrado")
    return {"ok": True}


def _to_response(entity: BancoEntity) -> BancoFormResponse:
    return BancoFormResponse(tid=entity.tid, nombre=entity.nombre, codigo=entity.codigo)
