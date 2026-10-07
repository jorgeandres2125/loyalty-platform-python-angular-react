"""Tests del cifrador de campos AES-256-GCM (Medida C — AP-0147 / AP-0095)."""
from __future__ import annotations

import os

import pytest

from src.domain.exceptions.cifrado_error import CifradoError
from src.infrastructure.security.aes_gcm_field_cipher import AesGcmFieldCipher

_AAD: str = "users_perfil_contacto|numero_de_cuenta|123456"


def _cipher(key_id: int = 1) -> AesGcmFieldCipher:
    return AesGcmFieldCipher({key_id: os.urandom(32)}, key_id)


def test_roundtrip_devuelve_el_valor_original() -> None:
    cipher: AesGcmFieldCipher = _cipher()
    cifrado: bytes | None = cipher.cifrar("0011223344", aad=_AAD)
    assert cifrado is not None
    assert cipher.descifrar(cifrado, aad=_AAD) == "0011223344"


def test_none_se_propaga_como_none() -> None:
    cipher: AesGcmFieldCipher = _cipher()
    assert cipher.cifrar(None, aad=_AAD) is None
    assert cipher.descifrar(None, aad=_AAD) is None


def test_cadena_vacia_hace_roundtrip() -> None:
    cipher: AesGcmFieldCipher = _cipher()
    cifrado: bytes | None = cipher.cifrar("", aad=_AAD)
    assert cifrado is not None
    assert cipher.descifrar(cifrado, aad=_AAD) == ""


def test_no_determinista_por_nonce_aleatorio() -> None:
    cipher: AesGcmFieldCipher = _cipher()
    a: bytes | None = cipher.cifrar("mismo", aad=_AAD)
    b: bytes | None = cipher.cifrar("mismo", aad=_AAD)
    assert a != b


def test_prefijo_version_y_key_id() -> None:
    cipher: AesGcmFieldCipher = AesGcmFieldCipher({7: os.urandom(32)}, 7)
    cifrado: bytes | None = cipher.cifrar("x", aad=_AAD)
    assert cifrado is not None
    assert cifrado[0] == 1   # versión de formato
    assert cifrado[1] == 7   # key_id activo


def test_aad_distinto_falla() -> None:
    cipher: AesGcmFieldCipher = _cipher()
    cifrado: bytes | None = cipher.cifrar("secreto", aad=_AAD)
    assert cifrado is not None
    with pytest.raises(CifradoError):
        cipher.descifrar(cifrado, aad="users_perfil_contacto|numero_de_cuenta|OTRA_PK")


def test_criptograma_manipulado_falla() -> None:
    cipher: AesGcmFieldCipher = _cipher()
    cifrado: bytes | None = cipher.cifrar("secreto", aad=_AAD)
    assert cifrado is not None
    manipulado: bytes = cifrado[:-1] + bytes([cifrado[-1] ^ 0x01])
    with pytest.raises(CifradoError):
        cipher.descifrar(manipulado, aad=_AAD)


def test_clave_incorrecta_falla() -> None:
    emisor: AesGcmFieldCipher = AesGcmFieldCipher({1: os.urandom(32)}, 1)
    otro: AesGcmFieldCipher = AesGcmFieldCipher({1: os.urandom(32)}, 1)
    cifrado: bytes | None = emisor.cifrar("secreto", aad=_AAD)
    assert cifrado is not None
    with pytest.raises(CifradoError):
        otro.descifrar(cifrado, aad=_AAD)


def test_rotacion_descifra_con_clave_retirada() -> None:
    clave_vieja: bytes = os.urandom(32)
    clave_nueva: bytes = os.urandom(32)
    viejo: AesGcmFieldCipher = AesGcmFieldCipher({1: clave_vieja}, 1)
    cifrado_viejo: bytes | None = viejo.cifrar("dato-antiguo", aad=_AAD)
    assert cifrado_viejo is not None
    # El cifrador nuevo activa la clave 2 pero conserva la 1 (retirada) para leer.
    nuevo: AesGcmFieldCipher = AesGcmFieldCipher({1: clave_vieja, 2: clave_nueva}, 2)
    assert nuevo.descifrar(cifrado_viejo, aad=_AAD) == "dato-antiguo"
    assert nuevo.cifrar("nuevo", aad=_AAD)[1] == 2  # cifra con la clave activa


def test_key_id_desconocido_al_descifrar_falla() -> None:
    emisor: AesGcmFieldCipher = AesGcmFieldCipher({9: os.urandom(32)}, 9)
    cifrado: bytes | None = emisor.cifrar("x", aad=_AAD)
    assert cifrado is not None
    receptor: AesGcmFieldCipher = AesGcmFieldCipher({1: os.urandom(32)}, 1)
    with pytest.raises(CifradoError):
        receptor.descifrar(cifrado, aad=_AAD)


def test_clave_de_tamano_invalido_es_rechazada() -> None:
    with pytest.raises(CifradoError):
        AesGcmFieldCipher({1: os.urandom(16)}, 1)


def test_key_id_activo_ausente_es_rechazado() -> None:
    with pytest.raises(CifradoError):
        AesGcmFieldCipher({1: os.urandom(32)}, 2)


def test_criptograma_truncado_falla() -> None:
    cipher: AesGcmFieldCipher = _cipher()
    with pytest.raises(CifradoError):
        cipher.descifrar(b"\x01\x01abc", aad=_AAD)
