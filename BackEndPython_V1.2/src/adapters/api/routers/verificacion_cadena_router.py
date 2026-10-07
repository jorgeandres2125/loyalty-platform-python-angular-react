from __future__ import annotations

from fastapi import APIRouter, Depends

from src.adapters.api.schemas.cadena.verificar_cadena_request import VerificarCadenaRequest
from src.adapters.api.schemas.cadena.verificar_cadena_response import VerificarCadenaResponse
from src.application.use_cases.verificar_integridad_cadena_use_case import (
    VerificarIntegridadCadenaUseCase,
)
from src.domain.value_objects.eslabon_cadena import EslabonCadena
from src.domain.value_objects.resultado_verificacion_cadena import ResultadoVerificacionCadena
from src.infrastructure.config.dependencies import get_verificar_cadena_uc, require_token

# AP-0025: verificacion de integridad de la cadena de sellos de auditoria. Requiere JWT;
# un auditor envia los eslabones tal como quedaron en el destino inmutable (SIEM o WORM)
# y el sistema confirma que la cadena no fue alterada.
router: APIRouter = APIRouter()


@router.post(
    "/verificar-cadena",
    response_model=VerificarCadenaResponse,
    summary="Verificar la integridad de la cadena de sellos de auditoria (AP-0025)",
)
async def verificar_cadena(
    body: VerificarCadenaRequest,
    token: dict[str, object] = Depends(require_token),
    uc: VerificarIntegridadCadenaUseCase = Depends(get_verificar_cadena_uc),
) -> VerificarCadenaResponse:
    eslabones: list[EslabonCadena] = [
        EslabonCadena(
            secuencia=item.secuencia,
            hash_previo=item.hash_previo,
            hash_contenido=item.hash_contenido,
            hash_actual=item.hash_actual,
        )
        for item in body.eslabones
    ]
    resultado: ResultadoVerificacionCadena = uc.ejecutar(eslabones)
    mensaje: str = (
        "Cadena integra, los eventos no fueron alterados."
        if resultado.integra
        else "Cadena rota en la secuencia " + str(resultado.primer_roto) + "."
    )
    return VerificarCadenaResponse(
        integra=resultado.integra,
        total=resultado.total,
        primer_roto=resultado.primer_roto,
        motivo=resultado.motivo,
        mensaje=mensaje,
    )
