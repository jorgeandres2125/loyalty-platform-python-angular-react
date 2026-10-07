from __future__ import annotations

import secrets
from typing import Final

from src.domain.exceptions.custodia_insuficiente import CustodiaInsuficiente

# Reduccion del cuerpo finito GF(2^8), la de AES (x^8 + x^4 + x^3 + x + 1), byte 0x1B.
_REDUCCION: Final[int] = 0x1B


def _mul_lento(alfa: int, beta: int) -> int:
    producto: int = 0
    for _ in range(8):
        if beta & 1:
            producto ^= alfa
        alto: int = alfa & 0x80
        alfa = (alfa << 1) & 0xFF
        if alto:
            alfa ^= _REDUCCION
        beta >>= 1
    return producto


_EXP: Final[list[int]] = [0] * 512
_LOG: Final[list[int]] = [0] * 256


def _inicializar_tablas() -> None:
    valor: int = 1
    for indice in range(255):
        _EXP[indice] = valor
        _LOG[valor] = indice
        valor = _mul_lento(valor, 3)
    for indice in range(255, 512):
        _EXP[indice] = _EXP[indice - 255]


_inicializar_tablas()


def _mul(alfa: int, beta: int) -> int:
    if alfa == 0 or beta == 0:
        return 0
    return _EXP[_LOG[alfa] + _LOG[beta]]


def _div(alfa: int, beta: int) -> int:
    if beta == 0:
        raise CustodiaInsuficiente("division por cero en el cuerpo finito (shares invalidos)")
    if alfa == 0:
        return 0
    return _EXP[_LOG[alfa] - _LOG[beta] + 255]


class ShamirCustodiaCompartida:
    """AP-0015: reparto de secreto de Shamir sobre GF(256) para la doble custodia.

    Divide un secreto (la KEK) en `total` shares con un umbral: se necesitan `umbral`
    shares para reconstruirlo y menos de esos no revelan nada. Trabaja byte a byte, por
    cada byte del secreto genera un polinomio de grado umbral-1 con el byte como termino
    independiente y coeficientes aleatorios, y lo evalua en los puntos 1..total. Cada
    share es bytes con el formato [indice][imagen del byte 0][imagen del byte 1]...
    Satisface el puerto CustodiaCompartidaClave (PEP 544).
    """

    def dividir(self, secreto: bytes, total: int, umbral: int) -> list[bytes]:
        if not 2 <= umbral <= total <= 255:
            raise CustodiaInsuficiente(
                "parametros de reparto invalidos (se exige 2 <= umbral <= total <= 255)"
            )
        if not secreto:
            raise CustodiaInsuficiente("el secreto a repartir no puede ser vacio")
        shares: list[bytearray] = [bytearray([indice]) for indice in range(1, total + 1)]
        for byte in secreto:
            coeficientes: list[int] = [byte] + [
                secrets.randbelow(256) for _ in range(umbral - 1)
            ]
            for posicion, punto in enumerate(range(1, total + 1)):
                shares[posicion].append(self._evaluar(coeficientes, punto))
        return [bytes(share) for share in shares]

    def reconstruir(self, shares: list[bytes]) -> bytes:
        if len(shares) < 2:
            raise CustodiaInsuficiente("se requieren al menos 2 shares para reconstruir")
        longitud: int = len(shares[0]) - 1
        if longitud <= 0 or any(len(share) != longitud + 1 for share in shares):
            raise CustodiaInsuficiente("shares con formato o longitud inconsistente")
        puntos: list[int] = [share[0] for share in shares]
        if len(set(puntos)) != len(puntos):
            raise CustodiaInsuficiente("shares con indice repetido")
        secreto: bytearray = bytearray()
        for posicion in range(longitud):
            imagenes: list[int] = [share[1 + posicion] for share in shares]
            secreto.append(self._interpolar_en_cero(puntos, imagenes))
        return bytes(secreto)

    @staticmethod
    def _evaluar(coeficientes: list[int], punto: int) -> int:
        acumulador: int = 0
        for coeficiente in reversed(coeficientes):
            acumulador = _mul(acumulador, punto) ^ coeficiente
        return acumulador

    @staticmethod
    def _interpolar_en_cero(puntos: list[int], imagenes: list[int]) -> int:
        acumulador: int = 0
        for ii in range(len(puntos)):
            numerador: int = 1
            denominador: int = 1
            for jj in range(len(puntos)):
                if ii == jj:
                    continue
                numerador = _mul(numerador, puntos[jj])
                denominador = _mul(denominador, puntos[ii] ^ puntos[jj])
            acumulador ^= _mul(imagenes[ii], _div(numerador, denominador))
        return acumulador
