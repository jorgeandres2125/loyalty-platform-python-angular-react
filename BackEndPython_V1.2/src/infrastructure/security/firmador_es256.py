from __future__ import annotations

import hashlib
import logging

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from src.domain.exceptions.firma_invalida import FirmaInvalida
from src.domain.value_objects.algoritmo_firma import AlgoritmoFirma

_logger: logging.Logger = logging.getLogger("sufi.config")


class FirmadorEs256:
    """AP-0006: firma y verificacion ES256 (ECDSA P-256 con SHA-256) con cryptography.

    Satisface el puerto FirmadorDigital por estructura (PEP 544). En desarrollo, si no
    se inyecta una clave privada, genera una efimera por proceso (las firmas no
    sobreviven a un reinicio; util solo en desarrollo). En produccion la clave debe
    inyectarse por entorno o, mejor, delegarse a un KMS o HSM (operacion Sign remota)
    con un adaptador equivalente en interfaz. El kid es la huella SHA-256 de la clave
    publica; identifica la clave en el JWKS para la verificacion.
    """

    def __init__(self, clave_privada_pem: bytes | None) -> None:
        self.algoritmo: AlgoritmoFirma = AlgoritmoFirma.ES256
        self._privada: ec.EllipticCurvePrivateKey = self._cargar(clave_privada_pem)
        self._publica: ec.EllipticCurvePublicKey = self._privada.public_key()
        self.kid: str = self._calcular_kid(self._publica)

    @staticmethod
    def _cargar(clave_privada_pem: bytes | None) -> ec.EllipticCurvePrivateKey:
        if not clave_privada_pem:
            _logger.warning(
                "AP-0006: sin clave de firma configurada; se genero una clave ES256 "
                "efimera por proceso. Inyecte FIRMA_PRIVATE_KEY_PEM o use un KMS o HSM."
            )
            return ec.generate_private_key(ec.SECP256R1())
        try:
            cargada = serialization.load_pem_private_key(clave_privada_pem, password=None)
        except (ValueError, TypeError) as exc:
            raise FirmaInvalida("clave privada de firma invalida o ilegible") from exc
        if not isinstance(cargada, ec.EllipticCurvePrivateKey):
            raise FirmaInvalida("la clave de firma debe ser de curva eliptica (ES256)")
        return cargada

    @staticmethod
    def _calcular_kid(publica: ec.EllipticCurvePublicKey) -> str:
        der: bytes = publica.public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return hashlib.sha256(der).hexdigest()[:16]

    def firmar(self, mensaje: bytes) -> bytes:
        return self._privada.sign(mensaje, ec.ECDSA(hashes.SHA256()))

    def verificar(self, mensaje: bytes, firma: bytes) -> bool:
        try:
            self._publica.verify(firma, mensaje, ec.ECDSA(hashes.SHA256()))
            return True
        except InvalidSignature:
            return False
