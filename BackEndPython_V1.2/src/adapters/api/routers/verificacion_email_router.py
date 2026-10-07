from __future__ import annotations

from typing import Final

from fastapi import APIRouter, Depends, HTTPException, status

from src.adapters.api.schemas.verificacion_email.confirmar_codigo_request import (
    ConfirmarCodigoRequest,
)
from src.adapters.api.schemas.verificacion_email.confirmar_codigo_response import (
    ConfirmarCodigoResponse,
)
from src.adapters.api.schemas.verificacion_email.solicitar_codigo_request import (
    SolicitarCodigoRequest,
)
from src.adapters.api.schemas.verificacion_email.solicitar_codigo_response import (
    SolicitarCodigoResponse,
)
from src.application.dto.resultado_solicitud_codigo_dto import ResultadoSolicitudCodigoDTO
from src.application.use_cases.verificar_email_use_case import VerificarEmailUseCase
from src.domain.exceptions.codigo_invalido import CodigoInvalido
from src.infrastructure.config.dependencies import (
    get_verificacion_email_uc,
    require_throttle_humano,
)

# Router PÚBLICO (sin JWT): el doble opt-in es justamente lo que prueba la identidad
# del titular del correo durante el auto-registro. Protegido por cooldown de reenvío
# e intentos limitados en el caso de uso (AP-0004).
router: APIRouter = APIRouter()

# Mensaje único para todas las solicitudes — no distingue si el documento existe
# (anti-enumeración).
_MENSAJE_SOLICITUD: Final[str] = (
    "Si los datos corresponden a un registro con correo, enviamos un código de "
    "verificación de 8 dígitos. Revisa tu bandeja de entrada."
)


@router.post(
    "/solicitar",
    response_model=SolicitarCodigoResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Solicitar código de verificación de correo (AP-0004)",
    # AP-0019: gating de humano por retrasos incrementales por IP en el auto-registro,
    # además del cooldown/intentos del caso de uso (AP-0004).
    dependencies=[Depends(require_throttle_humano("registro"))],
)
async def solicitar_codigo(
    body: SolicitarCodigoRequest,
    uc: VerificarEmailUseCase = Depends(get_verificacion_email_uc),
) -> SolicitarCodigoResponse:
    resultado: ResultadoSolicitudCodigoDTO = await uc.solicitar_codigo_async(
        tipo_documento=body.tipo_documento,
        numero_documento=body.numero_documento,
    )
    return SolicitarCodigoResponse(
        enviado=resultado.enviado,
        mensaje=_MENSAJE_SOLICITUD,
        email_enmascarado=resultado.email_enmascarado,
        expira_en_horas=resultado.expira_en_horas,
    )


@router.post(
    "/confirmar",
    response_model=ConfirmarCodigoResponse,
    summary="Confirmar código de verificación de correo (AP-0004)",
)
async def confirmar_codigo(
    body: ConfirmarCodigoRequest,
    uc: VerificarEmailUseCase = Depends(get_verificacion_email_uc),
) -> ConfirmarCodigoResponse:
    try:
        await uc.confirmar_codigo_async(
            tipo_documento=body.tipo_documento,
            numero_documento=body.numero_documento,
            codigo=body.codigo,
        )
    except CodigoInvalido as exc:
        detalle: str = exc.motivo
        if exc.intentos_restantes is not None and exc.intentos_restantes > 0:
            detalle = f"{exc.motivo} Intentos restantes: {exc.intentos_restantes}."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detalle) from exc
    return ConfirmarCodigoResponse(
        verificado=True,
        mensaje="Correo verificado correctamente.",
    )
