from __future__ import annotations

from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, Depends, Response

from src.adapters.api.schemas.health.estado_disponibilidad_response import (
    EstadoDisponibilidadResponse,
)
from src.adapters.api.schemas.health.estado_sincronizacion_response import (
    EstadoSincronizacionResponse,
)
from src.application.dto.estado_sincronizacion_dto import EstadoSincronizacionDTO
from src.application.use_cases.verificar_sincronizacion_horaria_use_case import (
    VerificarSincronizacionHorariaUseCase,
)
from src.domain.ports.outbound.sonda_disponibilidad import SondaDisponibilidad
from src.infrastructure.config.dependencies import (
    SettingsDep,
    get_sonda_disponibilidad,
    get_verificar_sync_horaria_uc,
)

_VERSION: str = "1.2.0"

router = APIRouter()


@router.get("/hora", response_model=EstadoSincronizacionResponse)
async def estado_sincronizacion_horaria(
    settings: SettingsDep,
    uc: VerificarSincronizacionHorariaUseCase = Depends(get_verificar_sync_horaria_uc),
) -> EstadoSincronizacionResponse:
    """AP-0144: estado de sincronizacion de la hora del sistema con la hora oficial
    del pais. Endpoint de monitoreo: nunca falla por la API externa (degrada)."""
    ahora: datetime = datetime.now(UTC)
    if not settings.hora_sync_enabled:
        return EstadoSincronizacionResponse(
            verificacion_habilitada=False,
            hora_sistema=ahora,
            detalle="Verificacion de hora oficial deshabilitada.",
        )
    try:
        estado: EstadoSincronizacionDTO = await uc.ejecutar_async()
    except (httpx.HTTPError, ValueError) as exc:
        return EstadoSincronizacionResponse(
            verificacion_habilitada=True,
            hora_sistema=ahora,
            detalle=f"No se pudo consultar la hora oficial: {type(exc).__name__}.",
        )
    return EstadoSincronizacionResponse(
        verificacion_habilitada=True,
        hora_sistema=estado.hora_sistema,
        hora_oficial=estado.hora_oficial,
        desfase_segundos=estado.desfase_segundos,
        sincronizado=estado.sincronizado,
        umbral_segundos=estado.umbral_segundos,
    )


@router.get("/live", response_model=EstadoDisponibilidadResponse)
async def liveness() -> EstadoDisponibilidadResponse:
    """AP-0081: liveness probe. Confirma que el proceso esta vivo y respondiendo.
    No consulta dependencias externas: un fallo aqui indica que Kubernetes debe
    reiniciar la replica (restartPolicy)."""
    return EstadoDisponibilidadResponse(estado="vivo", version=_VERSION)


@router.get("/ready", response_model=EstadoDisponibilidadResponse)
async def readiness(
    response: Response,
    sonda: SondaDisponibilidad = Depends(get_sonda_disponibilidad),
) -> EstadoDisponibilidadResponse:
    """AP-0081: readiness probe. Verifica la conectividad con la base de datos;
    si no responde, devuelve 503 para que Kubernetes y el balanceador saquen la
    replica de rotacion sin reiniciarla (drena en caliente durante un failover de
    BD o un arranque incompleto)."""
    bd_ok: bool = await sonda.base_datos_disponible()
    if not bd_ok:
        response.status_code = 503
        return EstadoDisponibilidadResponse(
            estado="no-listo", version=_VERSION, base_datos=False
        )
    return EstadoDisponibilidadResponse(
        estado="listo", version=_VERSION, base_datos=True
    )
