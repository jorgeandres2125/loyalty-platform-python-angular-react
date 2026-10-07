from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.adapters.api.object_authz import autorizar_objeto
from src.adapters.api.schemas.firma.firmar_request import FirmarRequest
from src.adapters.api.schemas.firma.firmar_response import FirmarResponse
from src.adapters.api.schemas.firma.verificar_firma_request import VerificarFirmaRequest
from src.adapters.api.schemas.firma.verificar_firma_response import VerificarFirmaResponse
from src.application.dto.resultado_firma_dto import ResultadoFirmaDTO
from src.application.dto.resultado_verificacion_firma_dto import ResultadoVerificacionFirmaDTO
from src.application.services.authorization_service import AuthorizationService
from src.application.use_cases.firma_digital_use_case import FirmaDigitalUseCase
from src.domain.value_objects.accion_recurso import AccionRecurso
from src.domain.value_objects.resource_type import ResourceType
from src.infrastructure.config.dependencies import (
    get_authorization_service,
    get_firma_digital_uc,
    require_token,
)

# Router de firma digital (AP-0006). Requiere JWT: el emisor de la firma es el titular
# autenticado (claim 'sub'). La verificacion valida la firma ES256 sobre el payload.
router: APIRouter = APIRouter()


@router.post(
    "",
    response_model=FirmarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Firmar digitalmente un recurso o transaccion sensible (AP-0006)",
)
async def firmar(
    body: FirmarRequest,
    token: dict[str, object] = Depends(require_token),
    authz: AuthorizationService = Depends(get_authorization_service),
    uc: FirmaDigitalUseCase = Depends(get_firma_digital_uc),
) -> FirmarResponse:
    await autorizar_objeto(
        authz, token, ResourceType.EVIDENCIA_FIRMA, AccionRecurso.CREATE, None
    )
    emisor: str = str(token.get("sub", ""))
    resultado: ResultadoFirmaDTO = await uc.firmar_async(
        recurso_tipo=body.recurso_tipo,
        recurso_id=body.recurso_id,
        payload=body.payload,
        emisor=emisor,
    )
    return FirmarResponse(
        evidencia_id=resultado.evidencia_id,
        kid=resultado.kid,
        alg=resultado.alg,
        valor_firma=resultado.valor_firma,
        hash_payload=resultado.hash_payload,
        hash_evidencia=resultado.hash_evidencia,
        mensaje="Recurso firmado digitalmente (ES256).",
    )


@router.post(
    "/verificar",
    response_model=VerificarFirmaResponse,
    summary="Verificar una firma digital (AP-0006)",
)
async def verificar(
    body: VerificarFirmaRequest,
    token: dict[str, object] = Depends(require_token),
    uc: FirmaDigitalUseCase = Depends(get_firma_digital_uc),
) -> VerificarFirmaResponse:
    resultado: ResultadoVerificacionFirmaDTO = await uc.verificar_async(
        payload=body.payload, valor_firma=body.valor_firma
    )
    mensaje: str = "Firma valida." if resultado.valida else "Firma invalida o no coincide."
    return VerificarFirmaResponse(
        valida=resultado.valida, kid=resultado.kid, alg=resultado.alg, mensaje=mensaje
    )
