from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.adapters.api.object_authz import require_object_access
from src.adapters.api.schemas.oob.iniciar_desafio_request import IniciarDesafioRequest
from src.adapters.api.schemas.oob.iniciar_desafio_response import IniciarDesafioResponse
from src.adapters.api.schemas.oob.resolver_desafio_request import ResolverDesafioRequest
from src.adapters.api.schemas.oob.resolver_desafio_response import ResolverDesafioResponse
from src.application.dto.resultado_iniciar_oob_dto import ResultadoIniciarOobDTO
from src.application.dto.resultado_resolver_oob_dto import ResultadoResolverOobDTO
from src.application.use_cases.autorizacion_oob_use_case import AutorizacionOobUseCase
from src.domain.exceptions.desafio_oob_invalido import DesafioOobInvalido
from src.domain.value_objects.accion_recurso import AccionRecurso
from src.domain.value_objects.resource_type import ResourceType
from src.infrastructure.config.dependencies import get_autorizacion_oob_uc, require_token

# Router del subsistema de confirmacion fuera de banda (AP-0005). Requiere JWT: la
# transaccion critica la inicia un usuario ya autenticado y la confirmacion viaja por
# un canal independiente (correo). El uid del titular sale del claim 'sub' del token.
router: APIRouter = APIRouter()


@router.post(
    "/desafios",
    response_model=IniciarDesafioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar confirmacion fuera de banda de una transaccion critica (AP-0005)",
)
async def iniciar_desafio(
    body: IniciarDesafioRequest,
    token: dict[str, object] = Depends(require_token),
    uc: AutorizacionOobUseCase = Depends(get_autorizacion_oob_uc),
) -> IniciarDesafioResponse:
    uid: str = str(token.get("sub", ""))
    resultado: ResultadoIniciarOobDTO = await uc.iniciar_async(
        uid=uid,
        tipo_transaccion=body.tipo_transaccion.value,
        payload=body.payload,
    )
    mensaje: str
    if resultado.requiere_oob and not resultado.enviado:
        mensaje = "No fue posible enviar la confirmacion: no hay un canal disponible."
    elif resultado.requiere_oob:
        mensaje = "Enviamos un codigo de confirmacion a tu correo. Apruebalo para continuar."
    else:
        mensaje = "La operacion no requiere confirmacion adicional."
    return IniciarDesafioResponse(
        requiere_oob=resultado.requiere_oob,
        enviado=resultado.enviado,
        desafio_id=resultado.desafio_id,
        estado=resultado.estado,
        canal=resultado.canal,
        email_enmascarado=resultado.email_enmascarado,
        expira_en_segundos=resultado.expira_en_segundos,
        mensaje=mensaje,
    )


@router.post(
    "/desafios/{desafio_id}/resolver",
    response_model=ResolverDesafioResponse,
    summary="Aprobar o rechazar un desafio OOB (AP-0005)",
    dependencies=[
        Depends(
            require_object_access(
                ResourceType.DESAFIO_OOB, AccionRecurso.RESOLVE, "desafio_id"
            )
        )
    ],
)
async def resolver_desafio(
    desafio_id: str,
    body: ResolverDesafioRequest,
    token: dict[str, object] = Depends(require_token),
    uc: AutorizacionOobUseCase = Depends(get_autorizacion_oob_uc),
) -> ResolverDesafioResponse:
    uid: str = str(token.get("sub", ""))
    try:
        resultado: ResultadoResolverOobDTO = await uc.resolver_async(
            desafio_id=desafio_id, uid=uid, aprobar=body.aprobar, codigo=body.codigo
        )
    except DesafioOobInvalido as exc:
        detalle: str = exc.motivo
        if exc.intentos_restantes is not None and exc.intentos_restantes > 0:
            detalle = f"{exc.motivo} Intentos restantes: {exc.intentos_restantes}."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detalle) from exc
    mensaje: str = "Operacion confirmada." if resultado.aprobado else "Operacion rechazada."
    return ResolverDesafioResponse(
        estado=resultado.estado,
        aprobado=resultado.aprobado,
        tipo_transaccion=resultado.tipo_transaccion,
        payload_hash=resultado.payload_hash,
        mensaje=mensaje,
    )
