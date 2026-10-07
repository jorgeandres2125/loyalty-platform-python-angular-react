from __future__ import annotations

from fastapi import APIRouter, Depends

from src.adapters.api.schemas.dispositivo.dispositivo_response import DispositivoResponse
from src.application.services.servicio_dispositivo import ServicioDispositivo
from src.domain.entities.dispositivo_usuario import DispositivoUsuario
from src.infrastructure.config.dependencies import get_servicio_dispositivo, require_token

# AP-0014: trazabilidad â€” el usuario autenticado consulta sus equipos de acceso conocidos.
router: APIRouter = APIRouter()


@router.get(
    "/dispositivos",
    response_model=list[DispositivoResponse],
    summary="Mis dispositivos de acceso conocidos (AP-0014)",
)
async def mis_dispositivos(
    token_payload: dict[str, object] = Depends(require_token),
    servicio: ServicioDispositivo = Depends(get_servicio_dispositivo),
) -> list[DispositivoResponse]:
    uid: int = int(str(token_payload.get("sub", 0)))
    dispositivos: list[DispositivoUsuario] = await servicio.listar_por_usuario_async(uid)
    return [
        DispositivoResponse(
            device_hash=disp.device_hash,
            device_name=disp.device_name,
            user_agent=disp.user_agent,
            first_login=disp.first_login_iso,
            last_login=disp.last_login_iso,
            veces_visto=disp.veces_visto,
            trusted=disp.trusted,
        )
        for disp in dispositivos
    ]
