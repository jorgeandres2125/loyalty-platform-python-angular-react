"""Tests para los helpers de autorización en me_router (sin BD, sin HTTP)."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from src.adapters.api.routers.me_router import (
    _exigir_rol_comisionista,
    _exigir_rol_movilidad,
    _roles_de_token,
    _uid_de_token,
)

# ── _uid_de_token ──────────────────────────────────────────────────────────

def test_uid_de_token_parsea_sub_string() -> None:
    assert _uid_de_token({"sub": "42"}) == 42


def test_uid_de_token_acepta_sub_numerico() -> None:
    assert _uid_de_token({"sub": 7}) == 7


def test_uid_de_token_lanza_401_si_sub_no_parseable() -> None:
    with pytest.raises(HTTPException) as exc:
        _uid_de_token({"sub": "abc"})
    assert exc.value.status_code == 401


# ── _roles_de_token ────────────────────────────────────────────────────────

def test_roles_de_token_retorna_set_normalizado() -> None:
    assert _roles_de_token({"roles": ["comisionista", "asesor_consumo"]}) == {"comisionista", "asesor_consumo"}


def test_roles_de_token_lista_vacia_si_no_hay_claim() -> None:
    assert _roles_de_token({}) == set()


def test_roles_de_token_lista_vacia_si_tipo_invalido() -> None:
    assert _roles_de_token({"roles": "no-es-lista"}) == set()


# ── _exigir_rol_comisionista ──────────────────────────────────────────────

def test_exigir_rol_comisionista_acepta_movilidad() -> None:
    _exigir_rol_comisionista({"roles": ["comisionista"]})  # no raise


def test_exigir_rol_comisionista_acepta_consumo_con_underscore() -> None:
    """El JWT lleva el slug con underscore, no el nombre legacy con espacios."""
    _exigir_rol_comisionista({"roles": ["comisionista_consumo"]})  # no raise


def test_exigir_rol_comisionista_rechaza_admin() -> None:
    with pytest.raises(HTTPException) as exc:
        _exigir_rol_comisionista({"roles": ["administrator"]})
    assert exc.value.status_code == 403


def test_exigir_rol_comisionista_rechaza_sin_roles() -> None:
    with pytest.raises(HTTPException) as exc:
        _exigir_rol_comisionista({})
    assert exc.value.status_code == 403


# ── _exigir_rol_movilidad ─────────────────────────────────────────────────

def test_exigir_rol_movilidad_acepta_solo_movilidad() -> None:
    _exigir_rol_movilidad({"roles": ["comisionista"]})


def test_exigir_rol_movilidad_rechaza_comisionista_consumo() -> None:
    """Consumo no tiene perfil tributario ni documentos."""
    with pytest.raises(HTTPException) as exc:
        _exigir_rol_movilidad({"roles": ["comisionista_consumo"]})
    assert exc.value.status_code == 403


def test_exigir_rol_movilidad_rechaza_admin() -> None:
    with pytest.raises(HTTPException) as exc:
        _exigir_rol_movilidad({"roles": ["administrator"]})
    assert exc.value.status_code == 403
