from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.adapters.api.schemas.bloqueo.bloqueo_duro_request import BloqueoDuroRequest
from src.adapters.api.schemas.bloqueo.bloqueo_suave_request import BloqueoSuaveRequest
from src.adapters.api.schemas.bloqueo.estado_bloqueo_response import (
    EstadoBloqueoResponse,
)
from src.application.services.servicio_bloqueo_cuenta import ServicioBloqueoCuenta
from src.application.services.servicio_bloqueo_duro import ServicioBloqueoDuro
from src.domain.entities.bloqueo_cuenta import BloqueoCuenta
from src.domain.entities.bloqueo_duro import BloqueoDuro
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.value_objects.permiso import Permiso
from src.infrastructure.config.dependencies import (
    SessionDep,
    get_estado_credencial_repo_sesion,
    get_servicio_bloqueo_cuenta,
    get_servicio_bloqueo_duro,
    require_token,
)
from src.infrastructure.config.permission_dependencies import (
    actor_desde_token,
    require_permission,
)
from src.infrastructure.persistence.repositories.sqlalchemy_usuario_repo import (
    SQLAlchemyUsuarioRepo,
)
from src.shared.constants.bloqueo_duro import MOTIVO_SOFT_AUTOMATICO

# AP-0157: gestion administrativa del bloqueo suave (AP-0009) y del bloqueo duro. El duro
# tiene precedencia absoluta y solo lo retira quien tenga USUARIOS_HARDLOCK_GESTIONAR.
router: APIRouter = APIRouter()

_HARDLOCK = Depends(require_permission(Permiso.USUARIOS_HARDLOCK_GESTIONAR, estricto=True))
_SOFTLOCK = Depends(require_permission(Permiso.USUARIOS_SOFTLOCK_GESTIONAR, estricto=True))
_CONSULTA = Depends(
    require_permission(
        Permiso.USUARIOS_HARDLOCK_GESTIONAR,
        Permiso.USUARIOS_SOFTLOCK_GESTIONAR,
        estricto=True,
    )
)


async def _clave_de_uid(session: SessionDep, uid: int) -> str:
    """Resuelve el nombre de usuario normalizado (clave del bloqueo suave) desde el uid;
    404 si la cuenta no existe."""
    repo: SQLAlchemyUsuarioRepo = SQLAlchemyUsuarioRepo(session)
    usuario: UsuarioEntity | None = await repo.obtener_cualquiera_por_uid_async(uid)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario.nombre.strip().lower()


@router.post(
    "/{uid}/bloqueo-duro",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[_HARDLOCK],
    summary="Aplicar un bloqueo duro a una cuenta (AP-0157)",
)
async def aplicar_bloqueo_duro(
    uid: int,
    body: BloqueoDuroRequest,
    session: SessionDep,
    token: dict = Depends(require_token),
    servicio: ServicioBloqueoDuro = Depends(get_servicio_bloqueo_duro),
) -> None:
    actor_uid: int = actor_desde_token(token)[0]
    await servicio.aplicar(uid=uid, motivo=body.motivo, por_uid=actor_uid)
    # AP-0049: aplicar un bloqueo duro revoca en el acto las sesiones vivas del usuario.
    await get_estado_credencial_repo_sesion(session).incrementar_version(uid)


@router.delete(
    "/{uid}/bloqueo-duro",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[_HARDLOCK],
    summary="Remover el bloqueo duro de una cuenta (AP-0157, permiso especial)",
)
async def remover_bloqueo_duro(
    uid: int,
    token: dict = Depends(require_token),
    servicio: ServicioBloqueoDuro = Depends(get_servicio_bloqueo_duro),
) -> None:
    actor_uid: int = actor_desde_token(token)[0]
    await servicio.remover(uid=uid, por_uid=actor_uid)


@router.post(
    "/{uid}/bloqueo-suave",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[_SOFTLOCK],
    summary="Aplicar un bloqueo suave administrativo a una cuenta (AP-0157)",
)
async def aplicar_bloqueo_suave(
    uid: int,
    body: BloqueoSuaveRequest,
    session: SessionDep,
    servicio: ServicioBloqueoCuenta = Depends(get_servicio_bloqueo_cuenta),
) -> None:
    clave: str = await _clave_de_uid(session, uid)
    await servicio.bloquear_manual(clave, body.duracion_minutos, body.motivo)


@router.delete(
    "/{uid}/bloqueo-suave",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[_SOFTLOCK],
    summary="Cancelar el bloqueo suave de una cuenta (AP-0157)",
)
async def cancelar_bloqueo_suave(
    uid: int,
    session: SessionDep,
    servicio: ServicioBloqueoCuenta = Depends(get_servicio_bloqueo_cuenta),
) -> None:
    clave: str = await _clave_de_uid(session, uid)
    await servicio.desbloquear(clave)


@router.get(
    "/{uid}/estado-bloqueo",
    response_model=EstadoBloqueoResponse,
    dependencies=[_CONSULTA],
    summary="Consultar el estado de bloqueo (suave y duro) de una cuenta (AP-0157)",
)
async def estado_bloqueo(
    uid: int,
    session: SessionDep,
    servicio_suave: ServicioBloqueoCuenta = Depends(get_servicio_bloqueo_cuenta),
    servicio_duro: ServicioBloqueoDuro = Depends(get_servicio_bloqueo_duro),
) -> EstadoBloqueoResponse:
    clave: str = await _clave_de_uid(session, uid)
    suave: BloqueoCuenta | None = await servicio_suave.consultar(clave)
    duro: BloqueoDuro | None = await servicio_duro.consultar(uid)
    is_soft: bool = suave is not None and suave.bloqueada
    is_hard: bool = duro is not None and duro.activo
    return EstadoBloqueoResponse(
        uid=uid,
        is_soft_locked=is_soft,
        soft_lock_reason=(
            (suave.motivo or MOTIVO_SOFT_AUTOMATICO) if is_soft and suave is not None else None
        ),
        soft_lock_expiration_epoch=(
            suave.expira_en_epoch if is_soft and suave is not None and suave.expira_en_epoch > 0.0
            else None
        ),
        is_hard_locked=is_hard,
        hard_lock_reason=duro.motivo if is_hard and duro is not None else None,
    )
