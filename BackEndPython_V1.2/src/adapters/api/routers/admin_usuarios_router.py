from __future__ import annotations

from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from src.adapters.api.schemas.admin.usuarios.estado_cuenta_request import EstadoCuentaRequest
from src.adapters.api.schemas.admin.usuarios.password_temporal_request import (
    PasswordTemporalRequest,
)
from src.adapters.api.schemas.admin.usuarios.password_temporal_response import (
    PasswordTemporalResponse,
)
from src.adapters.api.schemas.admin.usuarios.usuario_list_item import UsuarioListItem
from src.adapters.api.schemas.admin.usuarios.usuario_list_response import UsuarioListResponse
from src.application.dto.usuario_list_dto import UsuarioListDTO
from src.application.use_cases.emitir_password_temporal_use_case import (
    EmitirPasswordTemporalUseCase,
)
from src.application.use_cases.gestionar_usuarios_use_case import GestionarUsuariosUseCase
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.permiso_denegado import PermisoDenegado
from src.domain.value_objects.origen_password_temporal import OrigenPasswordTemporal
from src.domain.value_objects.rol_usuario import RolUsuario
from src.infrastructure.config.dependencies import (
    SettingsDep,
    extraer_ip_cliente,
    get_admin_usuarios_uc,
    get_emitir_password_temporal_uc,
    get_security_audit_logger,
    get_servicio_auditoria,
)
from src.infrastructure.config.permission_dependencies import (
    actor_desde_token,
    require_admin_usuarios,
)
from src.infrastructure.logging.security_audit import SecurityAuditLogger
from src.shared.constants.auditoria import (
    ACCION_PASSWORD_TEMPORAL_EMITIDA,
    ACCION_USUARIO_ELIMINADO,
    ENTIDAD_PASSWORD_TEMPORAL,
)

router: APIRouter = APIRouter(dependencies=[Depends(require_admin_usuarios)])

_PAGE_SIZE_MAX: Final[int] = 100

# Ruta de emision de temporal (segmento variable: uid del usuario destino).
_RUTA_PASSWORD_TEMPORAL: Final[str] = '/{uid}/password-temporal'


@router.get(
    "",
    response_model=UsuarioListResponse,
    summary="Lista paginada de cuentas de usuario (Panel de Control)",
)
async def listar_usuarios(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=_PAGE_SIZE_MAX)] = 10,
    texto: Annotated[str | None, Query(max_length=200)] = None,
    activo: Annotated[bool | None, Query()] = None,
    uc: GestionarUsuariosUseCase = Depends(get_admin_usuarios_uc),
) -> UsuarioListResponse:
    result: UsuarioListDTO = await uc.listar_async(
        page=page,
        page_size=page_size,
        texto=texto,
        activo=activo,
    )
    items: list[UsuarioListItem] = [
        UsuarioListItem(
            uid=item.uid,
            nombre=item.nombre,
            email=item.email,
            activo=item.activo,
            roles=item.roles,
        )
        for item in result.items
    ]
    return UsuarioListResponse(
        items=items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.patch(
    "/{uid}/estado",
    response_model=UsuarioListItem,
    summary="Habilitar o deshabilitar una cuenta de usuario (AP-0001)",
)
async def cambiar_estado_usuario(
    uid: int,
    body: EstadoCuentaRequest,
    token: dict = Depends(require_admin_usuarios),
    uc: GestionarUsuariosUseCase = Depends(get_admin_usuarios_uc),
) -> UsuarioListItem:
    actor_uid: int
    actor_roles: list[RolUsuario]
    actor_uid, actor_roles = actor_desde_token(token)
    try:
        entity: UsuarioEntity = await uc.cambiar_estado_async(
            uid_objetivo=uid,
            activo=body.activo,
            actor_uid=actor_uid,
            actor_roles=actor_roles,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except PermisoDenegado as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    return _to_item(entity)


@router.post(
    _RUTA_PASSWORD_TEMPORAL,
    response_model=PasswordTemporalResponse,
    summary="Emitir una contrasena temporal para un usuario (AP-0047)",
)
async def emitir_password_temporal(
    uid: int,
    body: PasswordTemporalRequest,
    request: Request,
    settings: SettingsDep,
    token: dict = Depends(require_admin_usuarios),
    uc: EmitirPasswordTemporalUseCase = Depends(get_emitir_password_temporal_uc),
    audit: SecurityAuditLogger = Depends(get_security_audit_logger),
) -> PasswordTemporalResponse:
    # AP-0047 y AP-0048: genera una temporal (bcrypt, TTL con techo de 120 min)
    # con el origen completo del emisor. La clave en claro solo viaja en esta
    # respuesta (se muestra una unica vez); el sistema persiste su hash.
    actor_uid: int
    actor_uid, _ = actor_desde_token(token)
    actor_nombre: str = str(token.get("nombre", ""))
    ip: str = extraer_ip_cliente(request, settings)
    if not settings.password_temporal_habilitado:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La emision de contrasenas temporales esta deshabilitada",
        )
    try:
        entidad, clave, usuario = await uc.ejecutar_async(
            uid_objetivo=uid,
            emitida_por_uid=actor_uid,
            emitida_por_usuario=actor_nombre,
            origen=OrigenPasswordTemporal(body.origen),
            motivo=body.motivo,
            ip_emision=ip,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    audit.cambio_credencial(
        exito=True,
        actor=str(actor_uid),
        ip=ip,
        detalle=f"emision de contrasena temporal para uid={uid} (AP-0047)",
    )
    await get_servicio_auditoria().registrar_async(
        accion=ACCION_PASSWORD_TEMPORAL_EMITIDA,
        user_id=uid,
        usuario=usuario.nombre,
        ip_origen=ip,
        entidad=ENTIDAD_PASSWORD_TEMPORAL,
        entidad_id=str(entidad.id) if entidad.id is not None else None,
        detalle={
            "emitida_por_uid": actor_uid,
            "emitida_por_usuario": actor_nombre,
            "origen": entidad.origen.value,
            "motivo": entidad.motivo,
            "expira_iso": entidad.expira_iso,
        },
    )
    return PasswordTemporalResponse(
        uid=uid,
        usuario=usuario.nombre,
        password_temporal=clave,
        expira_iso=entidad.expira_iso,
        ttl_minutos=settings.password_temporal_ttl_minutos,
    )


@router.delete(
    "/{uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar (logicamente) una cuenta de usuario (AP-0049)",
)
async def eliminar_usuario(
    uid: int,
    request: Request,
    settings: SettingsDep,
    token: dict = Depends(require_admin_usuarios),
    uc: GestionarUsuariosUseCase = Depends(get_admin_usuarios_uc),
) -> None:
    # AP-0049: eliminacion logica (status = 0) mas revocacion inmediata de las
    # sesiones vivas (token_version++). Sin borrado fisico de dbo.users
    # (retencion AP-0026 e integridad referencial legacy).
    actor_uid: int
    actor_roles: list[RolUsuario]
    actor_uid, actor_roles = actor_desde_token(token)
    ip: str = extraer_ip_cliente(request, settings)
    try:
        objetivo: UsuarioEntity = await uc.eliminar_async(
            uid_objetivo=uid,
            actor_uid=actor_uid,
            actor_roles=actor_roles,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except PermisoDenegado as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    await get_servicio_auditoria().registrar_async(
        accion=ACCION_USUARIO_ELIMINADO,
        user_id=uid,
        usuario=objetivo.nombre,
        ip_origen=ip,
        detalle={"actor_uid": actor_uid},
    )


def _to_item(entity: UsuarioEntity) -> UsuarioListItem:
    return UsuarioListItem(
        uid=entity.uid if entity.uid is not None else 0,
        nombre=entity.nombre,
        email=entity.email,
        activo=entity.activo,
        roles=[rol.value for rol in entity.roles],
    )
