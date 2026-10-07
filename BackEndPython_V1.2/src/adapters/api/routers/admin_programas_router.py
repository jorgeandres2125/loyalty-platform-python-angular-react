from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.adapters.api.schemas.admin.programas.admin_programa_form_request import (
    AdminProgramaFormRequest,
)
from src.adapters.api.schemas.admin.programas.admin_programa_response import (
    AdminProgramaResponse,
)
from src.application.dto.admin_programa_form_dto import AdminProgramaFormDTO
from src.application.use_cases.gestionar_admin_programas_use_case import (
    GestionarAdminProgramasUseCase,
)
from src.domain.entities.comisionista_programa_entity import (
    ComisionistaProgramaEntity,
)
from src.infrastructure.config.dependencies import get_admin_programas_uc
from src.infrastructure.config.permission_dependencies import require_admin_catalogos

router: APIRouter = APIRouter(dependencies=[Depends(require_admin_catalogos)])


@router.get(
    "",
    response_model=list[AdminProgramaResponse],
    summary="Lista de programas (solo lectura completa)",
)
async def listar_programas(
    uc: GestionarAdminProgramasUseCase = Depends(get_admin_programas_uc),
) -> list[AdminProgramaResponse]:
    entities: list[ComisionistaProgramaEntity] = await uc.listar_async()
    return [
        AdminProgramaResponse(cpid=e.cpid, cp_nombre=e.cp_nombre) for e in entities
    ]


@router.get(
    "/{cpid}", response_model=AdminProgramaResponse, summary="Obtener programa por cpid"
)
async def obtener_programa(
    cpid: int, uc: GestionarAdminProgramasUseCase = Depends(get_admin_programas_uc)
) -> AdminProgramaResponse:
    entity: ComisionistaProgramaEntity | None = await uc.obtener_async(cpid)
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Programa no encontrado"
        )
    return AdminProgramaResponse(cpid=entity.cpid, cp_nombre=entity.cp_nombre)


@router.put(
    "/{cpid}",
    response_model=AdminProgramaResponse,
    summary="Actualizar el nombre del programa (única operación permitida)",
)
async def actualizar_programa(
    cpid: int,
    body: AdminProgramaFormRequest,
    uc: GestionarAdminProgramasUseCase = Depends(get_admin_programas_uc),
) -> AdminProgramaResponse:
    dto: AdminProgramaFormDTO = AdminProgramaFormDTO(cp_nombre=body.cp_nombre)
    try:
        entity: ComisionistaProgramaEntity | None = await uc.actualizar_nombre_async(cpid, dto)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Programa no encontrado"
        )
    return AdminProgramaResponse(cpid=entity.cpid, cp_nombre=entity.cp_nombre)
