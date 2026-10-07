from __future__ import annotations

from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.adapters.api.auditoria_critica import auditar_operacion_critica
from src.adapters.api.schemas.ejecutivo.ejecutivo_form_request import EjecutivoFormRequest
from src.adapters.api.schemas.ejecutivo.ejecutivo_form_response import EjecutivoFormResponse
from src.adapters.api.schemas.ejecutivo.ejecutivo_list_item import EjecutivoListItem
from src.adapters.api.schemas.ejecutivo.ejecutivo_list_response import EjecutivoListResponse
from src.application.dto.ejecutivo_form_dto import EjecutivoFormDTO
from src.application.dto.ejecutivo_list_dto import EjecutivoListDTO
from src.application.services.servicio_auditoria import ServicioAuditoria
from src.application.use_cases.gestionar_ejecutivos_use_case import GestionarEjecutivosUseCase
from src.domain.entities.ejecutivo_entity import EjecutivoEntity
from src.infrastructure.config.dependencies import (
    TokenDep,
    get_ejecutivos_uc,
    get_servicio_auditoria,
)
from src.infrastructure.config.permission_dependencies import actor_desde_token
from src.shared.constants.perfiles_ejecutivo import PERFILES_EJECUTIVO_NOMBRES

router: APIRouter = APIRouter()

_PAGE_SIZE_MAX: Final[int] = 100


@router.get(
    "",
    response_model=EjecutivoListResponse,
    summary="Lista paginada de ejecutivos",
)
async def listar_ejecutivos(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    tipo_doc: Annotated[str | None, Query(max_length=10)] = None,
    documento: Annotated[str | None, Query(max_length=40)] = None,
    perfil: Annotated[str | None, Query(max_length=20)] = None,
    estado: Annotated[bool | None, Query()] = None,
    uc: GestionarEjecutivosUseCase = Depends(get_ejecutivos_uc),
) -> EjecutivoListResponse:
    result: EjecutivoListDTO = await uc.listar_async(
        page=page,
        page_size=page_size,
        tipo_doc=tipo_doc,
        documento=documento,
        perfil=perfil,
        estado=estado,
    )
    items: list[EjecutivoListItem] = [
        EjecutivoListItem(
            id=item.id,
            tipo_documento=item.tipo_documento,
            numero_documento=item.numero_documento,
            nombre_completo=item.nombre_completo,
            codigo_ejecutivo=item.codigo_ejecutivo,
            celular=item.celular,
            email=item.email,
            perfil=item.perfil,
            perfil_nombre=item.perfil_nombre,
            estado=item.estado,
        )
        for item in result.items
    ]
    return EjecutivoListResponse(
        items=items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.get(
    "/{ejecutivo_id}",
    response_model=EjecutivoFormResponse,
    summary="Obtener ejecutivo por ID",
)
async def obtener_ejecutivo(
    ejecutivo_id: int,
    uc: GestionarEjecutivosUseCase = Depends(get_ejecutivos_uc),
) -> EjecutivoFormResponse:
    entity: EjecutivoEntity | None = await uc.obtener_async(ejecutivo_id)
    if entity is None or entity.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ejecutivo no encontrado")
    return _to_response(entity)


@router.post(
    "",
    response_model=EjecutivoFormResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear ejecutivo",
)
async def crear_ejecutivo(
    token: TokenDep,
    body: EjecutivoFormRequest,
    uc: GestionarEjecutivosUseCase = Depends(get_ejecutivos_uc),
    auditoria: ServicioAuditoria = Depends(get_servicio_auditoria),
) -> EjecutivoFormResponse:
    dto: EjecutivoFormDTO = _to_dto(body)
    try:
        entity: EjecutivoEntity = await uc.crear_async(dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    actor_uid, _roles = actor_desde_token(token)
    await auditar_operacion_critica(
        auditoria, actor_uid, "crear_ejecutivo", "ejecutivo", str(entity.id)
    )
    return _to_response(entity)


@router.put(
    "/{ejecutivo_id}",
    response_model=EjecutivoFormResponse,
    summary="Actualizar ejecutivo",
)
async def actualizar_ejecutivo(
    token: TokenDep,
    ejecutivo_id: int,
    body: EjecutivoFormRequest,
    uc: GestionarEjecutivosUseCase = Depends(get_ejecutivos_uc),
    auditoria: ServicioAuditoria = Depends(get_servicio_auditoria),
) -> EjecutivoFormResponse:
    dto: EjecutivoFormDTO = _to_dto(body)
    try:
        entity: EjecutivoEntity | None = await uc.actualizar_async(ejecutivo_id, dto)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if entity is None or entity.id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ejecutivo no encontrado")
    actor_uid, _roles = actor_desde_token(token)
    await auditar_operacion_critica(
        auditoria, actor_uid, "actualizar_ejecutivo", "ejecutivo", str(entity.id)
    )
    return _to_response(entity)


def _to_dto(body: EjecutivoFormRequest) -> EjecutivoFormDTO:
    return EjecutivoFormDTO(
        tipo_documento=body.tipo_documento,
        numero_documento=body.numero_documento,
        nombre_completo=body.nombre_completo,
        codigo_ejecutivo=body.codigo_ejecutivo,
        email=body.email,
        celular=body.celular,
        perfil=body.perfil,
        estado=body.estado,
    )


def _to_response(entity: EjecutivoEntity) -> EjecutivoFormResponse:
    return EjecutivoFormResponse(
        id=entity.id or 0,
        tipo_documento=entity.tipo_documento,
        numero_documento=entity.numero_documento,
        nombre_completo=entity.nombre_completo,
        codigo_ejecutivo=entity.codigo_ejecutivo,
        celular=entity.celular,
        email=entity.email,
        perfil=entity.perfil,
        perfil_nombre=PERFILES_EJECUTIVO_NOMBRES.get(entity.perfil, entity.perfil),
        estado=entity.estado,
    )
