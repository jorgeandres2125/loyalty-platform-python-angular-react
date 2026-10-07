from __future__ import annotations

from typing import Final

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.domain.exceptions.cifrado_error import CifradoError
from src.shared.utils.vector_inicializacion import generar_iv

# Disposición del valor almacenado en VARBINARY:
#   [ ver(1B) ][ key_id(1B) ][ nonce(12B) ][ ciphertext + tag GCM(N) ]
_VERSION: Final[int] = 1
_NONCE_BYTES: Final[int] = 12
_PREFIJO_BYTES: Final[int] = 2          # ver + key_id
_OFFSET_CT: Final[int] = _PREFIJO_BYTES + _NONCE_BYTES


class AesGcmFieldCipher:
    """Cifrado de campos con AES-256-GCM (AEAD: confidencialidad + integridad).

    Satisface el puerto CifradorCampos por estructura (PEP 544). Soporta varias
    claves a la vez para rotación: cifra siempre con la clave activa y descifra
    resolviendo la clave por el key_id embebido en el criptograma.
    """

    def __init__(self, claves: dict[int, bytes], key_id_activo: int) -> None:
        if key_id_activo not in claves:
            raise CifradoError(f"key_id activo {key_id_activo} ausente del registro de claves")
        if not 0 <= key_id_activo <= 255:
            raise CifradoError("key_id debe estar en el rango 0..255")
        self._registro: dict[int, AESGCM] = {
            kid: AESGCM(self._validar_clave(kid, raw)) for kid, raw in claves.items()
        }
        self._key_id_activo: int = key_id_activo

    @staticmethod
    def _validar_clave(key_id: int, raw: bytes) -> bytes:
        if len(raw) != 32:
            raise CifradoError(f"la clave {key_id} debe ser de 32 bytes (AES-256), no {len(raw)}")
        return raw

    def cifrar(self, claro: str | None, *, aad: str) -> bytes | None:
        if claro is None:
            return None
        nonce: bytes = generar_iv(_NONCE_BYTES)
        aes: AESGCM = self._registro[self._key_id_activo]
        ct: bytes = aes.encrypt(nonce, claro.encode("utf-8"), aad.encode("utf-8"))
        return bytes([_VERSION, self._key_id_activo]) + nonce + ct

    def descifrar(self, cifrado: bytes | None, *, aad: str) -> str | None:
        if cifrado is None:
            return None
        if len(cifrado) < _OFFSET_CT:
            raise CifradoError("criptograma demasiado corto o corrupto")
        key_id: int = cifrado[1]
        aes: AESGCM | None = self._registro.get(key_id)
        if aes is None:
            raise CifradoError(f"clave {key_id} desconocida (¿clave retirada sin re-cifrar?)")
        nonce: bytes = cifrado[_PREFIJO_BYTES:_OFFSET_CT]
        ct: bytes = cifrado[_OFFSET_CT:]
        try:
            return aes.decrypt(nonce, ct, aad.encode("utf-8")).decode("utf-8")
        except InvalidTag as exc:
            raise CifradoError(
                "tag GCM inválido (clave/AAD incorrectos o dato manipulado)"
            ) from exc
