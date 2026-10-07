"""AP-0092 -- descifrado de credenciales del archivo de configuracion."""
from __future__ import annotations

import base64
import binascii

from src.domain.exceptions.cifrado_error import CifradoError
from src.infrastructure.security.aes_gcm_field_cipher import AesGcmFieldCipher
from src.shared.constants.cifrado_config import (
    AAD_CONFIG_SECRETO,
    CONFIG_KEK_KEY_ID,
    ENC_PREFIJO_CONFIG,
)


class SecretDecryptor:
    """Descifra valores de configuracion marcados con `enc:gcm:` (AP-0092).

    Envuelve el motor AES-256-GCM (AP-0147) con la clave maestra (KEK) inyectada
    por entorno. Un valor sin el marcador se devuelve tal cual, de modo que el
    desarrollo local puede seguir usando texto plano sin KEK. Satisface, por
    estructura, cualquier consumidor que solo necesite `descifrar_valor`.
    """

    def __init__(self, kek: bytes | None) -> None:
        self._cifrador: AesGcmFieldCipher | None = (
            AesGcmFieldCipher({CONFIG_KEK_KEY_ID: kek}, CONFIG_KEK_KEY_ID)
            if kek is not None
            else None
        )

    @property
    def kek_configurada(self) -> bool:
        return self._cifrador is not None

    @staticmethod
    def esta_cifrado(valor: str) -> bool:
        return valor.startswith(ENC_PREFIJO_CONFIG)

    def descifrar_valor(self, valor: str) -> str:
        if not self.esta_cifrado(valor):
            return valor
        if self._cifrador is None:
            raise ValueError(
                "Hay un valor cifrado en la configuracion pero falta la clave "
                "maestra SUFI_CONFIG_KEK (AP-0092). Inyectela por entorno o "
                "Key Vault."
            )
        cuerpo: str = valor[len(ENC_PREFIJO_CONFIG):]
        try:
            blob: bytes = base64.b64decode(cuerpo, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError(
                "Valor cifrado de configuracion con base64 invalido (AP-0092)."
            ) from exc
        try:
            claro: str | None = self._cifrador.descifrar(blob, aad=AAD_CONFIG_SECRETO)
        except CifradoError as exc:
            raise ValueError(
                "No se pudo descifrar un valor de configuracion (AP-0092): "
                "clave maestra incorrecta o dato manipulado."
            ) from exc
        if claro is None:
            raise ValueError("Valor cifrado de configuracion vacio (AP-0092).")
        return claro

    def cifrar_valor(self, claro: str) -> str:
        if self._cifrador is None:
            raise ValueError(
                "No hay clave maestra SUFI_CONFIG_KEK para cifrar (AP-0092)."
            )
        blob: bytes | None = self._cifrador.cifrar(claro, aad=AAD_CONFIG_SECRETO)
        if blob is None:
            raise ValueError("No se pudo cifrar el valor de configuracion (AP-0092).")
        return ENC_PREFIJO_CONFIG + base64.b64encode(blob).decode("ascii")
