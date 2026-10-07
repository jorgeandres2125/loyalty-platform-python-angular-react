"""Constantes del SSO estandar OIDC/OAuth2 (AP-0010)."""
from typing import Final

# Algoritmo de firma OIDC por defecto (asimetrico, verificable via JWKS).
OIDC_ALG: Final[str] = "ES256"

# Algoritmos aceptados al validar tokens estandar. Se prohiben explicitamente los
# simetricos (HS256) y "none": no permiten validacion federada por JWKS.
ALGORITMOS_OIDC_PERMITIDOS: Final[frozenset[str]] = frozenset({"ES256", "RS256"})

# Rutas de los documentos estandar OpenID Connect.
RUTA_DISCOVERY: Final[str] = "/.well-known/openid-configuration"
RUTA_JWKS: Final[str] = "/.well-known/jwks.json"


# tipos declarados en el documento de descubrimiento.
SUBJECT_TYPES: Final[tuple[str, ...]] = ("public",)
RESPONSE_TYPES: Final[tuple[str, ...]] = ("token", "id_token")
GRANT_TYPES: Final[tuple[str, ...]] = ("authorization_code", "client_credentials")
SCOPES_SOPORTADOS: Final[tuple[str, ...]] = ("openid", "perfil", "roles")
CLAIMS_SOPORTADOS: Final[tuple[str, ...]] = ("sub", "iss", "aud", "exp", "iat", "roles", "scope")
