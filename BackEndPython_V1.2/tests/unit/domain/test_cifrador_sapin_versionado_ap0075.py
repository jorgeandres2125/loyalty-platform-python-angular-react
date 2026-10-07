from __future__ import annotations

import base64

import pytest

from src.domain.exceptions.token_sapin_invalido import TokenSapinInvalido
from src.domain.services.cifrador_sapin_versionado import CifradorSapinVersionado
from src.domain.services.crypto_sapin import CryptoSAPIN

_CLAVE_CTR: bytes = bytes(range(16))
_IV_CTR: bytes = bytes(range(16, 32))
_CLAVE_CBC: bytes = bytes(32)
_CLAVE_GCM: bytes = bytes(range(32))


def _crypto_v1() -> CryptoSAPIN:
    return CryptoSAPIN(aes_key_ctr=_CLAVE_CTR, aes_iv_ctr=_IV_CTR, aes_key_cbc=_CLAVE_CBC)


def test_v1_formato_intacto_byte_a_byte() -> None:
    crypto = _crypto_v1()
    versionado = CifradorSapinVersionado(crypto, None, "v1")
    esperado = crypto.generar_token_ctr("123", "Juan", "A1").token_cifrado
    obtenido = versionado.generar_token("123", "Juan", "A1").token_cifrado
    assert obtenido == esperado
    assert not obtenido.startswith("v2.")


def test_v2_round_trip_gcm_256() -> None:
    versionado = CifradorSapinVersionado(_crypto_v1(), _CLAVE_GCM, "v2")
    token = versionado.generar_token("123", "Juan", "A1").token_cifrado
    assert token.startswith("v2.")
    assert versionado.descifrar_v2(token) == "123|Juan|A1"


def test_v2_rechaza_token_manipulado() -> None:
    versionado = CifradorSapinVersionado(_crypto_v1(), _CLAVE_GCM, "v2")
    token = versionado.generar_token("123", "Juan", "A1").token_cifrado
    crudo = base64.urlsafe_b64decode(token[3:])
    alterado = crudo[:-1] + bytes([crudo[-1] ^ 1])
    manipulado = "v2." + base64.urlsafe_b64encode(alterado).decode("ascii")
    with pytest.raises(TokenSapinInvalido):
        versionado.descifrar_v2(manipulado)


def test_v2_exige_clave_de_32_bytes() -> None:
    with pytest.raises(ValueError):
        CifradorSapinVersionado(_crypto_v1(), bytes(16), "v2")


def test_v2_sin_clave_falla_al_construir() -> None:
    with pytest.raises(ValueError):
        CifradorSapinVersionado(_crypto_v1(), None, "v2")
