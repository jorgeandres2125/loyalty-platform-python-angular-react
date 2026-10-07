"""AP-0135 (OTP con longitud minima de 6) y AP-0136 (OTP con validez maxima de 60s).
Ambos verificables por codigo: piso de longitud garantizado al import y techo de TTL
forzado por la validacion de Settings."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.infrastructure.config.settings import Settings
from src.shared.constants.oob import OOB_CODIGO_LONGITUD
from src.shared.constants.otp import (
    OTP_LONGITUD_MINIMA,
    OTP_TTL_MAXIMO_SEG,
    validar_longitud_otp,
)
from src.shared.constants.otp_login import OTP_LOGIN_CODIGO_LONGITUD
from src.shared.constants.verificacion_email import CODIGO_LONGITUD

# ── AP-0135: longitud minima 6 ──


def test_piso_de_longitud_es_6() -> None:
    assert OTP_LONGITUD_MINIMA == 6


def test_todos_los_otp_cumplen_longitud_minima() -> None:
    assert OTP_LOGIN_CODIGO_LONGITUD >= OTP_LONGITUD_MINIMA
    assert OOB_CODIGO_LONGITUD >= OTP_LONGITUD_MINIMA
    assert CODIGO_LONGITUD >= OTP_LONGITUD_MINIMA


def test_validar_longitud_rechaza_menor_a_6() -> None:
    with pytest.raises(ValueError, match="AP-0135"):
        validar_longitud_otp(5, "PRUEBA")


def test_validar_longitud_acepta_6() -> None:
    assert validar_longitud_otp(6, "PRUEBA") == 6


# ── AP-0136: validez maxima 60s ──


def test_techo_de_ttl_es_60() -> None:
    assert OTP_TTL_MAXIMO_SEG == 60


def test_ttl_por_defecto_no_excede_60() -> None:
    s = Settings()
    assert s.otp_login_codigo_ttl_seg <= 60
    assert s.oob_codigo_ttl_seg <= 60


def test_ttl_login_mayor_a_60_es_rechazado() -> None:
    with pytest.raises(ValidationError):
        Settings(otp_login_codigo_ttl_seg=61)


def test_ttl_oob_mayor_a_60_es_rechazado() -> None:
    with pytest.raises(ValidationError):
        Settings(oob_codigo_ttl_seg=61)


def test_ttl_60_es_valido() -> None:
    s = Settings(otp_login_codigo_ttl_seg=60, oob_codigo_ttl_seg=60)
    assert s.otp_login_codigo_ttl_seg == 60
    assert s.oob_codigo_ttl_seg == 60
