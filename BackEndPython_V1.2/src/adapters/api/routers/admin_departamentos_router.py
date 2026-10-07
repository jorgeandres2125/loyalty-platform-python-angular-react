from __future__ import annotations

from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.api.schemas.admin.departamentos.departamento_form_request import (
    DepartamentoFormRequest,
)
from src.adapters.api.schemas.admin.departamentos.departamento_form_response import (
    DepartamentoFormResponse,
)
from src.adapters.api.schemas.admin.departamentos.departamento_list_item import (
    DepartamentoListItem,
)
from src.adapters.api.schemas.admin.departamentos.departamento_list_response import (
    DepartamentoListResponse,
)
from src.application.dto.departamento_form_dto import DepartamentoFormDTO
from src.application.dto.departamento_list_dto import DepartamentoListDTO
from src.application.use_cases.gestionar_departamentos_use_case import (
    GestionarDepartamentosUseCase,
)
from src.domain.entities.departamento_entity import DepartamentoEntity
from src.infrastructure.config.dependencies import get_admin_departamentos_uc
from src.infrastructure.config.permission_dependencies import require_admin_catalogos

router: APIRouter = APIRouter(dependencies=[Depends(require_admin_catalogos)])

_PAGE_SIZE_MAX: Final[int] = 100


@router.get("", response_model=DepartamentoListResponse, summary="Lista paginada de departamentos")
async def listar_departamentos(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    nombre: Annotated[str | None, Query(max_length=50)] = None,
    uc: GestionarDepartamentosUseCase = Depends(get_admin_departamentos_uc),
) -> DepartamentoListResponse:
    result: DepartamentoListDTO = await uc.listar_async(page=page, page_size=page_size, nombre=nombre)
    items: list[DepartamentoListItem] = [
        DepartamentoListItem(did=i.did, pid=i.pid, departamento=i.departamento)
        for i in result.items
    ]
    return DepartamentoListResponse(items=items, total=result.total, page=result.page, page_size=result.page_size)


@router.get("/{did}", response_model=DepartamentoFormResponse, summary="Obtener departamento por did")
async def obtener_departamento(
    did: int, uc: GestionarDepartamentosUseCase = Depends(get_admin_departamentos_uc)
) -> DepartamentoFormResponse:
    entity: DepartamentoEntity | None = await uc.obtener_async(did)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Departamento no encontrado")
    return _to_response(entity)


@router.post(
    "",
    response_model=DepartamentoFormResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo departamento",
)
async def crear_departamento(
    body: DepartamentoFormRequest,
    uc: GestionarDepartamentosUseCase = Depends(get_admin_departamentos_uc),
) -> DepartamentoFormResponse:
    dto: DepartamentoFormDTO = DepartamentoFormDTO(departamento=body.departamento, pid=body.pid)
    try:
        entity: DepartamentoEntity = await uc.crear_async(dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _to_response(entity)


@router.put("/{did}", response_model=DepartamentoFormResponse, summary="Actualizar un departamento")
async def actualizar_departamento(
    did: int,
    body: DepartamentoFormRequest,
    uc: GestionarDepartamentosUseCase = Depends(get_admin_departamentos_uc),
) -> DepartamentoFormResponse:
    dto: DepartamentoFormDTO = DepartamentoFormDTO(departamento=body.departamento, pid=body.pid)
    try:
        entity: DepartamentoEntity | None = await uc.actualizar_async(did, dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Departamento no encontrado")
    return _to_response(entity)


@router.delete("/{did}", status_code=status.HTTP_200_OK, summary="Eliminar un departamento")
async def eliminar_departamento(
    did: int, uc: GestionarDepartamentosUseCase = Depends(get_admin_departamentos_uc)
) -> dict[str, bool]:
    try:
        eliminado: bool = await uc.eliminar_async(did)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if not eliminado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Departamento no encontrado")
    return {"ok": True}


def _to_response(entity: DepartamentoEntity) -> DepartamentoFormResponse:
    return DepartamentoFormResponse(did=entity.did, pid=entity.pid, departamento=entity.departamento)
