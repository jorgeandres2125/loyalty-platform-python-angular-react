from __future__ import annotations

import base64
from datetime import datetime

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.domain.exceptions.token_sapin_invalido import TokenSapinInvalido
from src.domain.services.crypto_sapin import CryptoSAPIN
from src.domain.value_objects.token_sapin import TokenSAPIN
from src.shared.constants.sapin_token import (
    AAD_TOKEN_SAPIN,
    LONGITUD_CLAVE_GCM_BYTES,
    LONGITUD_NONCE_GCM_BYTES,
    PREFIJO_TOKEN_V2,
    SAPIN_TOKEN_V2,
)
from src.shared.security.secure_buffer import SecureBuffer
from src.shared.utils.vector_inicializacion import generar_iv


class CifradorSapinVersionado:
    """AP-0075: emisor versionado del token SAPIN.

    v1 = AES-128-CTR (contrato byte-a-byte con la plataforma externa MSP; formato intacto, sin
    marcador). v2 = AES-256-GCM (estandar corporativo, nonce unico por token mas tag de
    autenticacion, marcado con el prefijo de version). La version emitida la fija la
    configuracion; la validacion enruta por el marcador. Converger a v2 requiere coordinacion
    con MSP (dependencia externa): mientras tanto coexisten sin romper la integracion.
    """

    def __init__(
        self, crypto_v1: CryptoSAPIN, clave_gcm_v2: bytes | None, version: str
    ) -> None:
        if clave_gcm_v2 is not None and len(clave_gcm_v2) != LONGITUD_CLAVE_GCM_BYTES:
            raise ValueError("la clave GCM v2 debe ser de 32 bytes (AES-256)")
        if version == SAPIN_TOKEN_V2 and clave_gcm_v2 is None:
            raise ValueError(
                "SAPIN_AES_KEY_GCM (32 bytes) es obligatoria si SAPIN_TOKEN_VERSION es v2"
            )
        self._v1: CryptoSAPIN = crypto_v1
        self._clave_gcm_v2: bytes | None = clave_gcm_v2
        self._version: str = version

    def generar_token(self, cedula: str, nombre: str, alianza: str) -> TokenSAPIN:
        if self._version == SAPIN_TOKEN_V2:
            return self._generar_v2(cedula, nombre, alianza)
        return self._v1.generar_token_ctr(cedula, nombre, alianza)

    def _generar_v2(self, cedula: str, nombre: str, alianza: str) -> TokenSAPIN:
        if self._clave_gcm_v2 is None:
            raise TokenSapinInvalido("clave GCM v2 no configurada")
        nonce: bytes = generar_iv(LONGITUD_NONCE_GCM_BYTES)
        # AP-0080: el payload (PII) se mantiene en un SecureBuffer y se sobrescribe con ceros
        # inmediatamente tras cifrar (context manager).
        with SecureBuffer.desde_bytes(f"{cedula}|{nombre}|{alianza}".encode()) as sb:
            cifrado: bytes = AESGCM(self._clave_gcm_v2).encrypt(
                nonce, bytes(sb.vista()), AAD_TOKEN_SAPIN
            )
        token: str = PREFIJO_TOKEN_V2 + base64.urlsafe_b64encode(nonce + cifrado).decode("ascii")
        return TokenSAPIN(token_cifrado=token, cedula=cedula, generado_en=datetime.utcnow())

    def descifrar_v2(self, token: str) -> str:
        """Descifra y AUTENTICA un token v2 (AES-256-GCM). Los tokens v1 los valida la
        plataforma externa MSP (contrato legacy)."""
        if self._clave_gcm_v2 is None:
            raise TokenSapinInvalido("clave GCM v2 no configurada")
        if not token.startswith(PREFIJO_TOKEN_V2):
            raise TokenSapinInvalido("el token no es v2")
        crudo: bytes = base64.urlsafe_b64decode(token[len(PREFIJO_TOKEN_V2):])
        nonce: bytes = crudo[:LONGITUD_NONCE_GCM_BYTES]
        cifrado: bytes = crudo[LONGITUD_NONCE_GCM_BYTES:]
        try:
            payload: bytes = AESGCM(self._clave_gcm_v2).decrypt(nonce, cifrado, AAD_TOKEN_SAPIN)
        except InvalidTag as exc:
            raise TokenSapinInvalido(
                "tag GCM invalido: token manipulado o clave incorrecta"
            ) from exc
        return payload.decode()
