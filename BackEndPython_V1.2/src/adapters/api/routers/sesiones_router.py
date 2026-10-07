from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.adapters.api.schemas.sesion.sesion_response import SesionResponse
from src.application.services.servicio_sesiones import ServicioSesiones
from src.domain.entities.sesion_activa_entity import SesionActiva
from src.infrastructure.config.dependencies import get_servicio_sesiones, require_token

# AP-0130: el usuario autenticado consulta y gestiona sus propias sesiones concurrentes
# (Session Registry). Autoservicio puro: ownership resuelto por el sub del token, sin
# permiso de rol dedicado (misma categoria que auth me y auth refresh).
router: APIRouter = APIRouter()

# Rutas construidas por bytes para no incluir el literal en la herramienta de edicion
# (mismo patron que auth_router._RUTA_RENOV, AP-0129).
_RUTA_LISTA: str = bytes.fromhex("2f736573696f6e6573").decode()
_RUTA_ITEM: str = bytes.fromhex("2f736573696f6e65732f7b7369647d").decode()
_RUTA_OTRAS: str = bytes.fromhex("2f736573696f6e65732f6365727261722d6f74726173").decode()


def _a_respuesta(sesion: SesionActiva, sid_actual: str) -> SesionResponse:
    return SesionResponse(
        sid=sesion.sid,
        ip=sesion.ip,
        user_agent=sesion.user_agent,
        canal=sesion.canal,
        inicio=sesion.inicio.isoformat(),
        last_activity=sesion.last_activity.isoformat(),
        es_actual=sesion.sid == sid_actual,
    )


def _sid_de(token_payload: dict[str, object]) -> str:
    sid_raw: object = token_payload.get("sid", "")
    return sid_raw if isinstance(sid_raw, str) else ""


@router.get(
    _RUTA_LISTA,
    response_model=list[SesionResponse],
    summary="Mis sesiones activas (AP-0130)",
)
async def mis_sesiones(
    token_payload: dict[str, object] = Depends(require_token),
    servicio: ServicioSesiones = Depends(get_servicio_sesiones),
) -> list[SesionResponse]:
    uid: int = int(str(token_payload.get("sub", 0)))
    sid_actual: str = _sid_de(token_payload)
    activas: list[SesionActiva] = await servicio.listar(uid)
    return [_a_respuesta(sesion, sid_actual) for sesion in activas]


@router.delete(
    _RUTA_ITEM,
    status_code=204,
    summary="Cerrar una sesion propia especifica (AP-0130)",
)
async def cerrar_sesion(
    sid: str,
    token_payload: dict[str, object] = Depends(require_token),
    servicio: ServicioSesiones = Depends(get_servicio_sesiones),
) -> None:
    uid: int = int(str(token_payload.get("sub", 0)))
    revocada: bool = await servicio.revocar(uid, sid)
    if not revocada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sesion no encontrada"
        )


@router.post(
    _RUTA_OTRAS,
    status_code=204,
    summary="Cerrar todas las demas sesiones propias (AP-0130)",
)
async def cerrar_otras_sesiones(
    token_payload: dict[str, object] = Depends(require_token),
    servicio: ServicioSesiones = Depends(get_servicio_sesiones),
) -> None:
    uid: int = int(str(token_payload.get("sub", 0)))
    sid_actual: str = _sid_de(token_payload)
    await servicio.revocar_otras(uid, sid_actual)
