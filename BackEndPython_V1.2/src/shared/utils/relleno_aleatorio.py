from __future__ import annotations

import secrets
from typing import Final

# AP-0178: umbral de bytes bajo el cual se aplica relleno aleatorio.
UMBRAL_RELLENO: Final[int] = 32


def agregar_relleno(datos: bytes) -> bytes:
    """Prepend relleno aleatorio antes de cifrar con CBC.

    Formato: [1B pad_len][pad_len bytes aleatorios][datos]
    Si len(datos) < UMBRAL_RELLENO, pad_len >= UMBRAL_RELLENO - len(datos) + 1.
    Si len(datos) >= UMBRAL_RELLENO, pad_len en [1, 15] como ruido de longitud.
    """
    longitud: int = len(datos)
    if longitud < UMBRAL_RELLENO:
        pad_tam: int = UMBRAL_RELLENO - longitud + secrets.randbelow(16) + 1
    else:
        pad_tam = secrets.randbelow(15) + 1
    pad: bytes = secrets.token_bytes(pad_tam)
    return bytes([pad_tam]) + pad + datos


def quitar_relleno(datos_rellenos: bytes) -> bytes:
    """Extrae los datos originales quitando el relleno de agregar_relleno."""
    if not datos_rellenos:
        raise ValueError("datos vacios: no se puede quitar relleno")
    tam: int = datos_rellenos[0]
    if 1 + tam > len(datos_rellenos):
        raise ValueError("relleno invalido: longitud fuera de rango")
    return datos_rellenos[1 + tam:]
