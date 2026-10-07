from __future__ import annotations

import time

from src.application.dto.token_oidc_dto import TokenOidcDTO
from src.domain.ports.outbound.proveedor_clave_oidc import ProveedorClaveOidc


class EmitirTokenOidcUseCase:
    """AP-0010: emite un token estandar OIDC/OAuth2 (ES256) para un usuario autenticado.

    Genera un JWT con claims estandar (iss, sub, aud, iat, nbf, exp, scope, roles) firmado
    con la clave asimetrica del proveedor, verificable por cualquier Relying Party via el
    JWKS publicado. Es el artefacto de SSO estandar que unifica la autenticacion.
    """

    def __init__(
        self,
        proveedor: ProveedorClaveOidc,
        issuer: str,
        audiencia: str,
        ttl_segundos: int,
        scope_default: str,
    ) -> None:
        self._proveedor: ProveedorClaveOidc = proveedor
        self._issuer: str = issuer
        self._audiencia: str = audiencia
        self._ttl: int = ttl_segundos
        self._scope_default: str = scope_default

    def emitir(
        self,
        sub: str,
        roles: list[str],
        scope: str | None = None,
        token_version: int = 1,
    ) -> TokenOidcDTO:
        ahora: int = int(time.time())
        scope_efectivo: str = scope or self._scope_default
        claims: dict[str, object] = {
            "iss": self._issuer,
            "sub": sub,
            "aud": self._audiencia,
            "iat": ahora,
            "nbf": ahora,
            "exp": ahora + self._ttl,
            "scope": scope_efectivo,
            "roles": roles,
            # AP-0208: el token estandar porta la version de credencial vigente para que
            # un cambio de contrasena (token_version++) tambien lo invalide en el SSO.
            "tv": token_version,
        }
        return TokenOidcDTO(
            access_token=self._proveedor.firmar(claims),
            token_type="Bearer",
            expires_in=self._ttl,
            scope=scope_efectivo,
        )
