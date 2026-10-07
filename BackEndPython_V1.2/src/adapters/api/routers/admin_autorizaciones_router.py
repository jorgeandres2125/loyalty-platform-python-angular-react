from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict

from src.adapters.api.schemas.admin.autorizaciones.autorizacion_flags_request import (
    AutorizacionFlagsRequest,
)
from src.adapters.api.schemas.admin.autorizaciones.autorizacion_modulo_response import (
    AutorizacionModuloResponse,
)
from src.adapters.api.schemas.admin.autorizaciones.rol_response import RolResponse
from src.application.use_cases.gestionar_autorizaciones_use_case import (
    GestionarAutorizacionesUseCase,
)
from src.domain.entities.autorizacion_modulo_entity import AutorizacionModuloEntity
from src.domain.entities.rol_entity import RolEntity
from src.domain.value_objects.permisos_modulo import PermisosModulo
from src.infrastructure.config.dependencies import (
    extraer_ip_cliente,
    get_admin_autorizaciones_uc,
    get_security_audit_logger,
    get_settings,
)
from src.infrastructure.config.permission_dependencies import (
    actor_desde_token,
    require_admin_catalogos,
)
from src.infrastructure.logging.security_audit import SecurityAuditLogger

router: APIRouter = APIRouter(dependencies=[Depends(require_admin_catalogos)])


class _ModuloActivoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    activo: bool


def _to_response(ent: AutorizacionModuloEntity) -> AutorizacionModuloResponse:
    return AutorizacionModuloResponse(
        rid=ent.rid,
        module_id=ent.module_id,
        module_code=ent.module_code,
        module_nombre=ent.module_nombre,
        module_icono=ent.module_icono,
        module_activo=ent.module_activo,
        permission_id=ent.permission_id,
        puede_ver=ent.puede_ver,
        puede_crear=ent.puede_crear,
        puede_editar=ent.puede_editar,
        puede_eliminar=ent.puede_eliminar,
        puede_exportar=ent.puede_exportar,
        puede_aprobar=ent.puede_aprobar,
    )


@router.get("/roles", response_model=list[RolResponse], summary="Lista de roles del sistema")
async def listar_roles(
    uc: GestionarAutorizacionesUseCase = Depends(get_admin_autorizaciones_uc),
) -> list[RolResponse]:
    roles: list[RolEntity] = await uc.listar_roles_async()
    return [RolResponse(rid=r.rid, name=r.name) for r in roles]


@router.get(
    "/matriz/{rid}",
    response_model=list[AutorizacionModuloResponse],
    summary="Matriz de permisos de un rol (todos los módulos activos)",
)
async def obtener_matriz(
    rid: int,
    uc: GestionarAutorizacionesUseCase = Depends(get_admin_autorizaciones_uc),
) -> list[AutorizacionModuloResponse]:
    matriz: list[AutorizacionModuloEntity] = await uc.obtener_matriz_async(rid)
    return [_to_response(item) for item in matriz]


@router.put(
    "/matriz/{rid}/{module_id}",
    response_model=AutorizacionModuloResponse,
    summary="Actualizar los permisos de un rol sobre un módulo (upsert)",
)
async def actualizar_permisos(
    rid: int,
    module_id: int,
    body: AutorizacionFlagsRequest,
    request: Request,
    token: dict[str, object] = Depends(require_admin_catalogos),
    uc: GestionarAutorizacionesUseCase = Depends(get_admin_autorizaciones_uc),
    auditor: SecurityAuditLogger = Depends(get_security_audit_logger),
) -> AutorizacionModuloResponse:
    flags: PermisosModulo = PermisosModulo(
        puede_ver=body.puede_ver,
        puede_crear=body.puede_crear,
        puede_editar=body.puede_editar,
        puede_eliminar=body.puede_eliminar,
        puede_exportar=body.puede_exportar,
        puede_aprobar=body.puede_aprobar,
    )
    actor_uid: int
    actor_uid, _ = actor_desde_token(token)
    ip: str = extraer_ip_cliente(request, get_settings())
    recurso: str = f"frontend_modules_permissions rid={rid} module_id={module_id}"
    try:
        entidad: AutorizacionModuloEntity | None = await uc.actualizar_permisos_async(
            rid, module_id, flags
        )
    except ValueError as exc:
        auditor.cambio_autorizacion(
            exito=False, actor=str(actor_uid), ip=ip, recurso=recurso, detalle=str(exc)
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if entidad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Módulo no encontrado")
    auditor.cambio_autorizacion(
        exito=True, actor=str(actor_uid), ip=ip, recurso=recurso, detalle="actualizar permisos"
    )
    return _to_response(entidad)


@router.patch(
    "/modulos/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Activar o desactivar un módulo del frontend",
)
async def actualizar_activo_modulo(
    module_id: int,
    body: _ModuloActivoRequest,
    request: Request,
    token: dict[str, object] = Depends(require_admin_catalogos),
    uc: GestionarAutorizacionesUseCase = Depends(get_admin_autorizaciones_uc),
    auditor: SecurityAuditLogger = Depends(get_security_audit_logger),
) -> None:
    actor_uid: int
    actor_uid, _ = actor_desde_token(token)
    ip: str = extraer_ip_cliente(request, get_settings())
    recurso: str = f"frontend_modules module_id={module_id}"
    resultado = await uc.actualizar_activo_modulo_async(module_id, body.activo)
    if resultado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Módulo no encontrado")
    auditor.cambio_autorizacion(
        exito=True,
        actor=str(actor_uid),
        ip=ip,
        recurso=recurso,
        detalle=f"activo={body.activo}",
    )
