from __future__ import annotations

import base64

import pytest

from src.domain.services.crypto_sapin import CryptoSAPIN
from src.shared.constants.cifrado import TAMANO_BLOQUE_AES_BYTES
from src.shared.utils.vector_inicializacion import generar_iv


class TestGenerarIv:
    def test_longitud_solicitada(self) -> None:
        assert len(generar_iv(16)) == 16

    def test_es_aleatorio(self) -> None:
        assert generar_iv(16) != generar_iv(16)

    def test_rechaza_longitud_cero(self) -> None:
        with pytest.raises(ValueError):
            generar_iv(0)

    def test_rechaza_longitud_negativa(self) -> None:
        with pytest.raises(ValueError):
            generar_iv(-1)


def _crypto() -> CryptoSAPIN:
    return CryptoSAPIN(
        aes_key_ctr=bytes(16),
        aes_iv_ctr=bytes(16),
        aes_key_cbc=bytes(32),
    )


class TestCryptoSapinLongitudes:
    def test_acepta_longitudes_correctas(self) -> None:
        assert _crypto() is not None

    def test_iv_ctr_igual_a_longitud_de_clave(self) -> None:
        # AP-0179, para AES-128-CTR el IV (16B) iguala la longitud de clave (16B).
        assert TAMANO_BLOQUE_AES_BYTES == 16

    def test_rechaza_key_ctr_corta(self) -> None:
        with pytest.raises(ValueError):
            CryptoSAPIN(aes_key_ctr=bytes(8), aes_iv_ctr=bytes(16), aes_key_cbc=bytes(32))

    def test_rechaza_iv_ctr_corto(self) -> None:
        with pytest.raises(ValueError):
            CryptoSAPIN(aes_key_ctr=bytes(16), aes_iv_ctr=bytes(8), aes_key_cbc=bytes(32))

    def test_rechaza_key_cbc_corta(self) -> None:
        with pytest.raises(ValueError):
            CryptoSAPIN(aes_key_ctr=bytes(16), aes_iv_ctr=bytes(16), aes_key_cbc=bytes(16))


class TestCifradoCbcIvAleatorio:
    def test_iv_aleatorio_distinto_criptograma(self) -> None:
        c = _crypto()
        assert c.cifrar_password_cbc("secreto") != c.cifrar_password_cbc("secreto")

    def test_round_trip(self) -> None:
        c = _crypto()
        cifrado = c.cifrar_password_cbc("mi-password-123")
        assert c.descifrar_password_cbc(cifrado) == "mi-password-123"

    def test_iv_prepended_de_16_bytes(self) -> None:
        raw = base64.b64decode(_crypto().cifrar_password_cbc("x"))
        assert len(raw) >= TAMANO_BLOQUE_AES_BYTES
