from __future__ import annotations

from typing import Final

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.domain.exceptions.cifrado_error import CifradoError
from src.shared.utils.vector_inicializacion import generar_iv

_NONCE_BYTES: Final[int] = 12
_LONGITUD_KEK: Final[int] = 32


class KmsLocalSoftware:
    """Sustituto de software del KMS para desarrollo y pruebas (AP-0180).

    Custodia el KEK en un atributo privado y envuelve o desenvuelve DEKs con
    AES-256-GCM. NO es un HSM: respaldado_por_hsm es False, de modo que el guard
    de produccion lo rechaza (staging y produccion exigen un KMS o HSM real).
    Satisface por estructura el puerto GestorClaveMaestra (PEP 544).
    """

    def __init__(self, kek: bytes) -> None:
        if len(kek) != _LONGITUD_KEK:
            raise CifradoError("el KEK del KMS local debe ser de 32 bytes (AES-256)")
        self._aead: AESGCM = AESGCM(kek)

    @property
    def respaldado_por_hsm(self) -> bool:
        return False

    def cifrar_clave_datos(self, clave_datos: bytes) -> bytes:
        nonce: bytes = generar_iv(_NONCE_BYTES)
        return nonce + self._aead.encrypt(nonce, clave_datos, None)

    def descifrar_clave_datos(self, envoltura: bytes) -> bytes:
        if len(envoltura) <= _NONCE_BYTES:
            raise CifradoError("envoltura de clave demasiado corta o corrupta")
        nonce: bytes = envoltura[:_NONCE_BYTES]
        return self._aead.decrypt(nonce, envoltura[_NONCE_BYTES:], None)
