from __future__ import annotations

from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from src.adapters.api.schemas.admin.asignaciones.rol_asignable_response import (
    RolAsignableResponse,
)
from src.adapters.api.schemas.admin.asignaciones.rol_de_usuario_response import (
    RolDeUsuarioResponse,
)
from src.adapters.api.schemas.admin.asignaciones.usuario_cuenta_response import (
    UsuarioCuentaResponse,
)
from src.adapters.api.schemas.admin.asignaciones.usuarios_pagina_response import (
    UsuariosPaginaResponse,
)
from src.application.dto.pagina_usuarios_dto import PaginaUsuariosDTO
from src.application.use_cases.gestionar_asignacion_roles_use_case import (
    GestionarAsignacionRolesUseCase,
)
from src.domain.entities.rol_asignado_entity import RolAsignadoEntity
from src.domain.entities.rol_entity import RolEntity
from src.domain.entities.usuario_cuenta_entity import UsuarioCuentaEntity
from src.infrastructure.config.dependencies import (
    extraer_ip_cliente,
    get_admin_asignaciones_uc,
    get_security_audit_logger,
    get_settings,
)
from src.infrastructure.config.permission_dependencies import (
    actor_desde_token,
    require_admin_catalogos,
)
from src.infrastructure.logging.security_audit import SecurityAuditLogger

router: APIRouter = APIRouter(dependencies=[Depends(require_admin_catalogos)])

_PAGE_SIZE_MAX: Final[int] = 100


def _to_cuenta(e: UsuarioCuentaEntity) -> UsuarioCuentaResponse:
    return UsuarioCuentaResponse(uid=e.uid, nombre=e.nombre, email=e.email, activo=e.activo)


def _to_pagina(dto: PaginaUsuariosDTO) -> UsuariosPaginaResponse:
    return UsuariosPaginaResponse(
        items=[_to_cuenta(i) for i in dto.items],
        total=dto.total,
        page=dto.page,
        page_size=dto.page_size,
    )


@router.get("/roles", response_model=list[RolAsignableResponse], summary="Roles asignables")
async def listar_roles(
    uc: GestionarAsignacionRolesUseCase = Depends(get_admin_asignaciones_uc),
) -> list[RolAsignableResponse]:
    roles: list[RolEntity] = await uc.listar_roles_async()
    return [RolAsignableResponse(rid=r.rid, name=r.name) for r in roles]


@router.get(
    "/roles/{rid}/usuarios",
    response_model=UsuariosPaginaResponse,
    summary="Usuarios asignados a un rol (paginado)",
)
async def listar_usuarios_de_rol(
    rid: int,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    texto: Annotated[str | None, Query(max_length=200)] = None,
    uc: GestionarAsignacionRolesUseCase = Depends(get_admin_asignaciones_uc),
) -> UsuariosPaginaResponse:
    try:
        dto: PaginaUsuariosDTO = await uc.listar_usuarios_de_rol_async(rid, texto, page, page_size)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_pagina(dto)


@router.get(
    "/usuarios",
    response_model=UsuariosPaginaResponse,
    summary="Buscar cuentas de usuario (paginado)",
)
async def buscar_usuarios(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    texto: Annotated[str | None, Query(max_length=200)] = None,
    uc: GestionarAsignacionRolesUseCase = Depends(get_admin_asignaciones_uc),
) -> UsuariosPaginaResponse:
    dto: PaginaUsuariosDTO = await uc.buscar_usuarios_async(texto, page, page_size)
    return _to_pagina(dto)


@router.get(
    "/usuarios/{uid}/roles",
    response_model=list[RolDeUsuarioResponse],
    summary="Roles de un usuario (con marca de asignado)",
)
async def obtener_roles_de_usuario(
    uid: int,
    uc: GestionarAsignacionRolesUseCase = Depends(get_admin_asignaciones_uc),
) -> list[RolDeUsuarioResponse]:
    try:
        roles: list[RolAsignadoEntity] = await uc.obtener_roles_de_usuario_async(uid)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [RolDeUsuarioResponse(rid=r.rid, name=r.name, asignado=r.asignado) for r in roles]


@router.put(
    "/usuarios/{uid}/roles/{rid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Asignar un rol a un usuario (idempotente)",
)
async def asignar_rol(
    uid: int,
    rid: int,
    request: Request,
    token: dict[str, object] = Depends(require_admin_catalogos),
    uc: GestionarAsignacionRolesUseCase = Depends(get_admin_asignaciones_uc),
    auditor: SecurityAuditLogger = Depends(get_security_audit_logger),
) -> None:
    actor_uid: int
    actor_uid, _ = actor_desde_token(token)
    ip: str = extraer_ip_cliente(request, get_settings())
    recurso: str = f"users_roles uid={uid} rid={rid}"
    try:
        creado: bool = await uc.asignar_rol_async(actor_uid, uid, rid)
    except ValueError as exc:
        auditor.cambio_autorizacion(
            exito=False, actor=str(actor_uid), ip=ip, recurso=recurso, detalle=f"asignar: {exc}"
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    auditor.cambio_autorizacion(
        exito=True, actor=str(actor_uid), ip=ip, recurso=recurso,
        detalle="asignar" if creado else "asignar (ya existia)",
    )


@router.delete(
    "/usuarios/{uid}/roles/{rid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Quitar un rol de un usuario",
)
async def quitar_rol(
    uid: int,
    rid: int,
    request: Request,
    token: dict[str, object] = Depends(require_admin_catalogos),
    uc: GestionarAsignacionRolesUseCase = Depends(get_admin_asignaciones_uc),
    auditor: SecurityAuditLogger = Depends(get_security_audit_logger),
) -> None:
    actor_uid: int
    actor_uid, _ = actor_desde_token(token)
    ip: str = extraer_ip_cliente(request, get_settings())
    recurso: str = f"users_roles uid={uid} rid={rid}"
    try:
        await uc.quitar_rol_async(actor_uid, uid, rid)
    except ValueError as exc:
        auditor.cambio_autorizacion(
            exito=False, actor=str(actor_uid), ip=ip, recurso=recurso, detalle=f"quitar: {exc}"
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    auditor.cambio_autorizacion(
        exito=True, actor=str(actor_uid), ip=ip, recurso=recurso, detalle="quitar"
    )
