from __future__ import annotations

import base64
from typing import Final

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from src.shared.utils.relleno_aleatorio import agregar_relleno, quitar_relleno
from src.shared.utils.vector_inicializacion import generar_iv


class CifradoCbcConRelleno:
    """AES-256-CBC con relleno aleatorio para datos pequenos (AP-0178).

    Aplica relleno aleatorio antes de cifrar (AP-0178) y lo extrae al descifrar.
    No usar para rutas que requieran compatibilidad SAPIN legado (excluidas por
    contrato de migracion: deben ser byte-for-byte identicas al PHP original).
    """

    _BLOQUE: Final[int] = 16

    def __init__(self, clave: bytes) -> None:
        if len(clave) != 32:
            raise ValueError("clave debe ser 32 bytes (AES-256)")
        self._clave: bytes = clave

    def cifrar(self, dato: str) -> str:
        """Cifra dato con AES-256-CBC + relleno aleatorio. Retorna base64."""
        datos_bytes: bytes = dato.encode("utf-8")
        datos_rellenos: bytes = agregar_relleno(datos_bytes)
        datos_padded: bytes = pad(datos_rellenos, self._BLOQUE)
        iv: bytes = generar_iv(self._BLOQUE)
        cipher: object = AES.new(self._clave, AES.MODE_CBC, iv)
        cifrado: bytes = cipher.encrypt(datos_padded)
        return base64.b64encode(iv + cifrado).decode("ascii")

    def descifrar(self, cifrado_b64: str) -> str:
        """Descifra dato cifrado con cifrar()."""
        datos_cifrados: bytes = base64.b64decode(cifrado_b64)
        iv: bytes = datos_cifrados[:self._BLOQUE]
        cipher: object = AES.new(self._clave, AES.MODE_CBC, iv)
        datos_padded: bytes = cipher.decrypt(datos_cifrados[self._BLOQUE:])
        datos_rellenos: bytes = unpad(datos_padded, self._BLOQUE)
        return quitar_relleno(datos_rellenos).decode("utf-8")
