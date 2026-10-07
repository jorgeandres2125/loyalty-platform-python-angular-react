from __future__ import annotations

import base64
import secrets

import pytest

from src.application.services.servicio_custodia_compartida import ServicioCustodiaCompartida
from src.domain.exceptions.custodia_insuficiente import CustodiaInsuficiente
from src.infrastructure.config.settings import Settings
from src.infrastructure.security.shamir_custodia_compartida import ShamirCustodiaCompartida


def _shamir() -> ShamirCustodiaCompartida:
    return ShamirCustodiaCompartida()


def test_shamir_dos_de_tres_reconstruye_cualquier_par() -> None:
    sh = _shamir()
    kek: bytes = secrets.token_bytes(32)
    partes: list[bytes] = sh.dividir(kek, 3, 2)
    assert sh.reconstruir([partes[0], partes[1]]) == kek
    assert sh.reconstruir([partes[0], partes[2]]) == kek
    assert sh.reconstruir([partes[1], partes[2]]) == kek


def test_shamir_una_sola_share_no_reconstruye() -> None:
    sh = _shamir()
    kek: bytes = secrets.token_bytes(32)
    partes: list[bytes] = sh.dividir(kek, 3, 2)
    with pytest.raises(CustodiaInsuficiente):
        sh.reconstruir([partes[0]])


def test_shamir_share_alterada_no_recupera_la_kek() -> None:
    sh = _shamir()
    kek: bytes = secrets.token_bytes(32)
    partes: list[bytes] = sh.dividir(kek, 3, 2)
    alterada: bytes = bytes([partes[1][0]]) + bytes(b ^ 0xFF for b in partes[1][1:])
    assert sh.reconstruir([partes[0], alterada]) != kek


def test_shamir_umbral_tres_exige_tres_shares() -> None:
    sh = _shamir()
    kek: bytes = secrets.token_bytes(16)
    partes: list[bytes] = sh.dividir(kek, 5, 3)
    assert sh.reconstruir([partes[0], partes[2], partes[4]]) == kek
    assert sh.reconstruir([partes[0], partes[1]]) != kek


def test_shamir_parametros_invalidos() -> None:
    sh = _shamir()
    with pytest.raises(CustodiaInsuficiente):
        sh.dividir(b"x", 2, 3)
    with pytest.raises(CustodiaInsuficiente):
        sh.dividir(b"", 3, 2)


def _servicio(umbral: int = 2) -> ServicioCustodiaCompartida:
    return ServicioCustodiaCompartida(reparto=_shamir(), umbral=umbral)


def test_servicio_reconstruye_kek_con_umbral() -> None:
    svc = _servicio(2)
    kek: bytes = secrets.token_bytes(32)
    shares: list[str] = svc.dividir_kek(kek, 3)
    assert svc.reconstruir_kek([shares[0], shares[2]]) == kek


def test_servicio_fail_closed_con_menos_del_umbral() -> None:
    svc = _servicio(2)
    kek: bytes = secrets.token_bytes(32)
    shares: list[str] = svc.dividir_kek(kek, 3)
    with pytest.raises(CustodiaInsuficiente):
        svc.reconstruir_kek([shares[0]])
    with pytest.raises(CustodiaInsuficiente):
        svc.reconstruir_kek([shares[0], "   "])


def test_servicio_base64_invalido() -> None:
    svc = _servicio(2)
    with pytest.raises(CustodiaInsuficiente):
        svc.reconstruir_kek(["no-es-base64-!!!", "tampoco-@@@"])


def test_settings_doble_custodia_falla_sin_shares_suficientes() -> None:
    kek: bytes = secrets.token_bytes(32)
    shares: list[str] = _servicio(2).dividir_kek(kek, 3)
    with pytest.raises(ValueError):
        Settings(
            custodia_doble_enabled=True,
            custodia_umbral=2,
            custodia_shares=shares[0],
        )


def test_settings_doble_custodia_ok_con_shares_suficientes() -> None:
    kek: bytes = secrets.token_bytes(32)
    shares: list[str] = _servicio(2).dividir_kek(kek, 3)
    settings: Settings = Settings(
        custodia_doble_enabled=True,
        custodia_umbral=2,
        custodia_shares=shares[0] + "," + shares[1],
    )
    presentes: list[str] = [s for s in settings.custodia_shares.split(",") if s.strip()]
    reconstruida: bytes = _servicio(2).reconstruir_kek(presentes)
    assert base64.b64encode(reconstruida)  # la KEK se reconstruye sin excepcion


def test_settings_doble_custodia_deshabilitada_no_exige_shares() -> None:
    settings: Settings = Settings(custodia_doble_enabled=False)
    assert settings.custodia_doble_enabled is False
