from __future__ import annotations

import pytest

from src.shared.security.secure_buffer import SecureBuffer


def _ceros(cantidad: int) -> bytes:
    return bytes(cantidad)


def test_clear_sobrescribe_el_buffer_con_ceros() -> None:
    ba = bytearray(b"secreto-super-sensible")
    sb = SecureBuffer(ba)
    sb.clear()
    assert bytes(ba) == _ceros(len(ba))


def test_context_manager_limpia_al_salir() -> None:
    ba = bytearray(b"clave-de-sesion-123")
    with SecureBuffer(ba) as sb:
        assert sb.vista().tobytes() == b"clave-de-sesion-123"
    assert bytes(ba) == _ceros(len(ba))


def test_limpia_incluso_ante_excepcion() -> None:
    ba = bytearray(b"token-confidencial")
    with pytest.raises(RuntimeError):
        with SecureBuffer(ba):
            raise RuntimeError("fallo en medio del uso")
    assert bytes(ba) == _ceros(len(ba))


def test_repr_no_expone_el_secreto() -> None:
    sb = SecureBuffer(bytearray(b"secreto-visible"))
    texto = repr(sb)
    assert "secreto" not in texto
    assert "SecureBuffer" in texto


def test_vista_tras_clear_falla() -> None:
    sb = SecureBuffer(bytearray(b"abc"))
    sb.clear()
    with pytest.raises(ValueError):
        sb.vista()


def test_desde_bytes_construye_copia_utilizable() -> None:
    sb = SecureBuffer.desde_bytes(b"origen")
    assert sb.vista().tobytes() == b"origen"
    sb.clear()
