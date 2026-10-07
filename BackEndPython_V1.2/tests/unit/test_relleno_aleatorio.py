from __future__ import annotations

import secrets

import pytest

from src.infrastructure.security.cifrado_cbc_con_relleno import CifradoCbcConRelleno
from src.shared.utils.relleno_aleatorio import (
    UMBRAL_RELLENO,
    agregar_relleno,
    quitar_relleno,
)


class TestRellenoAleatorio:
    """AP-0178: relleno aleatorio para datos pequenos en CBC."""

    def test_round_trip_datos_pequenos(self) -> None:
        original: bytes = b"hola mundo"
        assert len(original) < UMBRAL_RELLENO
        resultado: bytes = agregar_relleno(original)
        assert quitar_relleno(resultado) == original

    def test_round_trip_datos_grandes(self) -> None:
        original: bytes = b"x" * 50
        assert len(original) >= UMBRAL_RELLENO
        resultado: bytes = agregar_relleno(original)
        assert quitar_relleno(resultado) == original

    def test_relleno_es_aleatorio(self) -> None:
        original: bytes = b"secreto"
        salida1: bytes = agregar_relleno(original)
        salida2: bytes = agregar_relleno(original)
        assert salida1 != salida2

    def test_datos_pequenos_superan_umbral(self) -> None:
        original: bytes = b"abc"
        resultado: bytes = agregar_relleno(original)
        assert len(resultado) > UMBRAL_RELLENO

    def test_vacios_lanza_error(self) -> None:
        with pytest.raises(ValueError):
            quitar_relleno(b"")


class TestCifradoCbcConRelleno:
    """AP-0178: CifradoCbcConRelleno usa relleno aleatorio."""

    def test_round_trip(self) -> None:
        clave: bytes = secrets.token_bytes(32)
        cifrador: CifradoCbcConRelleno = CifradoCbcConRelleno(clave)
        texto: str = "dato confidencial pequeno"
        assert cifrador.descifrar(cifrador.cifrar(texto)) == texto

    def test_seguridad_semantica(self) -> None:
        clave: bytes = secrets.token_bytes(32)
        cifrador: CifradoCbcConRelleno = CifradoCbcConRelleno(clave)
        cifrado1: str = cifrador.cifrar("hola")
        cifrado2: str = cifrador.cifrar("hola")
        assert cifrado1 != cifrado2

    def test_clave_invalida_lanza_error(self) -> None:
        with pytest.raises(ValueError):
            CifradoCbcConRelleno(secrets.token_bytes(16))
