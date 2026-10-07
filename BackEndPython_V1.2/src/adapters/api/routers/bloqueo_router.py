from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.adapters.api.schemas.bloqueo.desbloquear_request import DesbloquearRequest
from src.application.services.servicio_bloqueo_cuenta import ServicioBloqueoCuenta
from src.infrastructure.config.dependencies import (
    get_servicio_bloqueo_cuenta,
    require_token,
)

# AP-0009: desbloqueo manual de cuentas por un administrador. Requiere JWT. Complementa
# el desbloqueo automatico configurable; la clave es el nombre de usuario normalizado.
router: APIRouter = APIRouter()


@router.post(
    "/desbloquear",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_token)],
    summary="Desbloquear manualmente una cuenta bloqueada (AP-0009)",
)
async def desbloquear(
    body: DesbloquearRequest,
    servicio: ServicioBloqueoCuenta = Depends(get_servicio_bloqueo_cuenta),
) -> None:
    await servicio.desbloquear(body.username.strip().lower())
