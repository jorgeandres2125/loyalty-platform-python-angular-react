from fastapi import APIRouter, Depends

from src.adapters.api.object_authz import autorizar_objeto
from src.adapters.api.schemas.token_sapin_request_schema import TokenSAPINRequest
from src.adapters.api.schemas.token_sapin_response_schema import TokenSAPINResponse
from src.application.dto.token_sapin_request_dto import TokenSAPINRequestDTO
from src.application.services.authorization_service import AuthorizationService
from src.application.use_cases.generar_token_sapin_use_case import GenerarTokenSAPINUseCase
from src.domain.value_objects.accion_recurso import AccionRecurso
from src.domain.value_objects.resource_type import ResourceType
from src.infrastructure.config.dependencies import (
    TokenDep,
    get_authorization_service,
    get_token_sapin_uc,
)

router = APIRouter()


@router.post("/token", response_model=TokenSAPINResponse)
async def generar_token(
    token: TokenDep,
    body: TokenSAPINRequest,
    authz: AuthorizationService = Depends(get_authorization_service),
    uc: GenerarTokenSAPINUseCase = Depends(get_token_sapin_uc),
) -> TokenSAPINResponse:
    # AP-0052/AP-0055: el token SAPIN de incentivos es estrictamente personal (el
    # flujo Drupal legacy lo genera SIEMPRE para el usuario logueado, nunca para un
    # tercero). La autorizacion a nivel de objeto verifica la propiedad de la cedula:
    # un comisionista no puede pedir el token SSO de incentivos de OTRA persona (IDOR
    # hacia la plataforma externa SAPIN). No hay bypass de staff en este flujo.
    await autorizar_objeto(
        authz, token, ResourceType.TOKEN_SAPIN, AccionRecurso.CREATE, body.cedula
    )
    dto: TokenSAPINRequestDTO = TokenSAPINRequestDTO(cedula=body.cedula, alianza=body.alianza)
    result = await uc.ejecutar_async(dto)
    return TokenSAPINResponse(
        token=result.token, cedula=result.cedula, url_sapin=result.url_sapin
    )
