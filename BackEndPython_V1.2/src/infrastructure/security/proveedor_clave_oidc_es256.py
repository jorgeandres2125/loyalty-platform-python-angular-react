from __future__ import annotations

import base64
import hashlib
import logging

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from jose import jwt as jose_jwt

from src.domain.exceptions.token_oidc_invalido import TokenOidcInvalido
from src.shared.constants.oidc import OIDC_ALG

_logger: logging.Logger = logging.getLogger("sufi.config")


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


class ProveedorClaveOidcEs256:
    """AP-0010: proveedor de clave OIDC ES256 (ECDSA P-256) con cryptography + jose.

    Satisface el puerto ProveedorClaveOidc (PEP 544). Firma tokens estandar con ES256 y
    publica la clave publica como JWKS. En desarrollo, si no se inyecta clave, genera una
    efimera por proceso; en produccion la clave se inyecta por entorno o se delega a KMS
    o HSM (AP-0180). El kid es la huella SHA-256 de la clave publica.
    """

    def __init__(self, clave_privada_pem: bytes | None) -> None:
        self.algoritmo: str = OIDC_ALG
        self._privada: ec.EllipticCurvePrivateKey = self._cargar(clave_privada_pem)
        self._privada_pem: str = self._privada.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode("ascii")
        self._publica: ec.EllipticCurvePublicKey = self._privada.public_key()
        self._publica_pem: str = self._publica.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("ascii")
        self.kid: str = self._calcular_kid(self._publica)

    @staticmethod
    def _cargar(pem: bytes | None) -> ec.EllipticCurvePrivateKey:
        if not pem:
            _logger.warning(
                "AP-0010: sin clave OIDC configurada; se genero una ES256 efimera por "
                "proceso. Inyecte OIDC_SIGNING_KEY_PEM o use un KMS o HSM."
            )
            return ec.generate_private_key(ec.SECP256R1())
        try:
            cargada = serialization.load_pem_private_key(pem, password=None)
        except (ValueError, TypeError) as exc:
            raise TokenOidcInvalido("clave OIDC invalida o ilegible") from exc
        if not isinstance(cargada, ec.EllipticCurvePrivateKey):
            raise TokenOidcInvalido("la clave OIDC debe ser de curva eliptica (ES256)")
        return cargada

    @staticmethod
    def _calcular_kid(publica: ec.EllipticCurvePublicKey) -> str:
        der: bytes = publica.public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return hashlib.sha256(der).hexdigest()[:16]

    def firmar(self, claims: dict[str, object]) -> str:
        return str(
            jose_jwt.encode(
                claims,
                self._privada_pem,
                algorithm=self.algoritmo,
                headers={"kid": self.kid},
            )
        )

    def clave_publica_pem(self) -> str:
        return self._publica_pem

    def jwks(self) -> dict[str, object]:
        numeros = self._publica.public_numbers()
        coord_x: bytes = numeros.x.to_bytes(32, "big")
        coord_y: bytes = numeros.y.to_bytes(32, "big")
        return {
            "keys": [
                {
                    "kty": "EC",
                    "crv": "P-256",
                    "x": _b64url(coord_x),
                    "y": _b64url(coord_y),
                    "use": "sig",
                    "alg": self.algoritmo,
                    "kid": self.kid,
                }
            ]
        }
