from __future__ import annotations

from fastapi import APIRouter, Depends

from src.adapters.api.schemas.oidc.token_oidc_response import TokenOidcResponse
from src.application.dto.token_oidc_dto import TokenOidcDTO
from src.application.use_cases.emitir_token_oidc_use_case import EmitirTokenOidcUseCase
from src.domain.ports.outbound.proveedor_clave_oidc import ProveedorClaveOidc
from src.infrastructure.config.dependencies import (
    SettingsDep,
    get_emitir_token_oidc_uc,
    get_proveedor_clave_oidc,
    require_token,
)
from src.shared.constants.oidc import (
    CLAIMS_SOPORTADOS,
    GRANT_TYPES,
    OIDC_ALG,
    RESPONSE_TYPES,
    RUTA_DISCOVERY,
    RUTA_JWKS,
    SCOPES_SOPORTADOS,
    SUBJECT_TYPES,
)

# AP-0010: SSO estandar OIDC/OAuth2. discovery y jwks son publicos (los consulta cualquier
# Relying Party para validar los tokens); el token endpoint requiere sesion valida.
router: APIRouter = APIRouter()


@router.get(RUTA_DISCOVERY, summary="Descubrimiento OpenID Connect (AP-0010)")
async def discovery(settings: SettingsDep) -> dict[str, object]:
    base: str = settings.oidc_issuer.rstrip("/")
    return {
        "issuer": base,
        "authorization_endpoint": base + "/api/v1/auth/login",
        "token_endpoint": base + "/api/v1/oidc/token",
        "jwks_uri": base + RUTA_JWKS,
        "userinfo_endpoint": base + "/api/v1/me",
        "response_types_supported": list(RESPONSE_TYPES),
        "subject_types_supported": list(SUBJECT_TYPES),
        "id_token_signing_alg_values_supported": [OIDC_ALG],
        "grant_types_supported": list(GRANT_TYPES),
        "scopes_supported": list(SCOPES_SOPORTADOS),
        "claims_supported": list(CLAIMS_SOPORTADOS),
    }


@router.get(RUTA_JWKS, summary="JWKS de firma OIDC (AP-0010)")
async def jwks(
    proveedor: ProveedorClaveOidc = Depends(get_proveedor_clave_oidc),
) -> dict[str, object]:
    return proveedor.jwks()


@router.post(
    "/api/v1/oidc/token",
    response_model=TokenOidcResponse,
    summary="Emitir un token estandar OIDC/OAuth2 para el usuario autenticado (AP-0010)",
)
async def emitir_token(
    token_payload: dict[str, object] = Depends(require_token),
    uc: EmitirTokenOidcUseCase = Depends(get_emitir_token_oidc_uc),
) -> TokenOidcResponse:
    sub: str = str(token_payload.get("sub", ""))
    roles_crudo: object = token_payload.get("roles", [])
    roles: list[str] = (
        [str(rol) for rol in roles_crudo] if isinstance(roles_crudo, list) else []
    )
    # AP-0208: el tv de la sesion que solicita el token se propaga al token estandar;
    # asi un cambio de contrasena posterior lo invalida tambien en las aplicaciones SSO.
    tv_crudo: object = token_payload.get("tv", 1)
    token_version: int = tv_crudo if isinstance(tv_crudo, int) else 1
    dto: TokenOidcDTO = uc.emitir(sub=sub, roles=roles, token_version=token_version)
    return TokenOidcResponse(
        access_token=dto.access_token,
        token_type=dto.token_type,
        expires_in=dto.expires_in,
        scope=dto.scope,
    )
