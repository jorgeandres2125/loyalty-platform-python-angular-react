from __future__ import annotations

from jose import JWTError
from jose import jwt as jose_jwt

from src.domain.exceptions.token_oidc_invalido import TokenOidcInvalido
from src.domain.ports.outbound.proveedor_clave_oidc import ProveedorClaveOidc
from src.shared.constants.oidc import ALGORITMOS_OIDC_PERMITIDOS


class ValidadorTokenEstandar:
    """AP-0010: valida correctamente un token estandar OIDC/OAuth2.

    Verifica la firma con la clave publica (la del JWKS), el emisor (iss), la audiencia
    (aud) y la vigencia (exp, nbf, iat), y exige que el algoritmo sea asimetrico permitido
    (rechaza none y HS*, que no permiten validacion federada). Fail-closed: cualquier
    fallo lanza TokenOidcInvalido. Es la validacion que exige el control AP-0010.
    """

    def __init__(self, proveedor: ProveedorClaveOidc, issuer: str, audiencia: str) -> None:
        self._proveedor: ProveedorClaveOidc = proveedor
        self._issuer: str = issuer
        self._audiencia: str = audiencia

    def validar(self, token: str) -> dict[str, object]:
        try:
            header: dict[str, object] = jose_jwt.get_unverified_header(token)
        except JWTError as exc:
            raise TokenOidcInvalido("token ilegible") from exc
        alg: object = header.get("alg")
        if not isinstance(alg, str) or alg not in ALGORITMOS_OIDC_PERMITIDOS:
            raise TokenOidcInvalido("algoritmo de firma no permitido")
        try:
            claims: dict[str, object] = jose_jwt.decode(
                token,
                self._proveedor.clave_publica_pem(),
                algorithms=list(ALGORITMOS_OIDC_PERMITIDOS),
                issuer=self._issuer,
                audience=self._audiencia,
            )
        except JWTError as exc:
            raise TokenOidcInvalido("token invalido (" + str(exc) + ")") from exc
        return claims
