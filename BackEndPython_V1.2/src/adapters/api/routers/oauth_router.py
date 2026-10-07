from __future__ import annotations

from fastapi import APIRouter, Depends

from src.adapters.api.schemas.oauth.token_oauth_request import TokenOAuthRequest
from src.adapters.api.schemas.oauth.token_oauth_response import TokenOAuthResponse
from src.application.dto.token_oauth_dto import TokenOAuthDTO
from src.application.use_cases.emitir_token_oauth_use_case import EmitirTokenOAuthUseCase
from src.infrastructure.config.dependencies import TokenDep, get_emitir_token_oauth_uc

router = APIRouter()


@router.post('/token', response_model=TokenOAuthResponse)
async def emitir_token_oauth(
    body: TokenOAuthRequest,
    token: TokenDep,
    uc: EmitirTokenOAuthUseCase = Depends(get_emitir_token_oauth_uc),
) -> TokenOAuthResponse:
    '''AP-0146: nuestro IdP emite un access token estandar para una app de terceros
    SOLO tras autenticarse el usuario en nuestro front (TokenDep lo exige).'''
    sub: str = str(token.get('sub', ''))
    roles_raw = token.get('roles') or []
    roles: list[str] = [str(rol) for rol in roles_raw]
    dto: TokenOAuthDTO = uc.emitir(sub=sub, audiencia=body.audience, roles=roles, scope=body.scope)
    return TokenOAuthResponse(
        access_token=dto.access_token,
        token_type=dto.token_type,
        expires_in=dto.expires_in,
        scope=dto.scope,
        audience=dto.audience,
    )
