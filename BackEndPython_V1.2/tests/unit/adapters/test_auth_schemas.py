"""Tests para los schemas Pydantic de autenticación (sin 'permisos', con 'modulos')."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.adapters.api.schemas.cambio_password_schema import CambioPasswordRequest
from src.adapters.api.schemas.me_response_schema import MeResponse
from src.adapters.api.schemas.modulo_permiso_schema import ModuloPermisoSchema
from src.adapters.api.schemas.token_response_schema import TokenResponse
from src.shared.constants.password_policy import (
    PASSWORD_MIN_LONGITUD_USUARIO_FINAL,
    PASSWORD_MIN_TIPOS_CARACTER,
    contar_tipos_caracter,
)

# Contraseña que cumple longitud (>=12) y complejidad (4 tipos): minúscula,
# mayúscula, dígito y especial. Base para los tests que necesitan una clave válida.
PASSWORD_VALIDA: str = "Abcdefghij1!"


def _modulo_dict() -> dict:
    return {
        "module_id": 1,
        "module_code": "DASHBOARD",
        "nombre": "Dashboard",
        "ruta": "/dashboard",
        "icono": "bi-speedometer2",
        "orden": 10,
        "puede_ver": True,
        "puede_crear": False,
        "puede_editar": False,
        "puede_eliminar": False,
        "puede_exportar": False,
        "puede_aprobar": False,
    }


# ── ModuloPermisoSchema ─────────────────────────────────────────────────────

def test_modulo_permiso_schema_valida_payload_minimo() -> None:
    m = ModuloPermisoSchema(**_modulo_dict())
    assert m.module_code == "DASHBOARD"


def test_modulo_permiso_schema_no_acepta_module_padre_id() -> None:
    """Catálogo plano: extra='forbid' debe rechazar el legacy module_padre_id."""
    payload = _modulo_dict() | {"module_padre_id": 5}
    with pytest.raises(ValidationError):
        ModuloPermisoSchema(**payload)


def test_modulo_permiso_schema_rechaza_extra_campo() -> None:
    payload = _modulo_dict() | {"foo": "bar"}
    with pytest.raises(ValidationError):
        ModuloPermisoSchema(**payload)


# ── TokenResponse ───────────────────────────────────────────────────────────

def test_token_response_no_tiene_campo_permisos() -> None:
    """Decisión de diseño post-2026-05-19: se eliminó 'permisos[]', solo 'modulos[]'."""
    assert "permisos" not in TokenResponse.model_fields


def test_token_response_tiene_campos_uid_username_email_roles_modulos() -> None:
    campos = set(TokenResponse.model_fields.keys())
    esperados = {"access_token", "token_type", "uid", "username", "email", "roles", "modulos"}
    assert esperados.issubset(campos)


def test_token_response_construye_con_modulos() -> None:
    r = TokenResponse(
        access_token="xyz",
        uid=1,
        username="alice",
        email="a@b.co",
        roles=["administrator"],
        modulos=[ModuloPermisoSchema(**_modulo_dict())],
    )
    assert r.token_type == "bearer"
    assert len(r.modulos) == 1
    assert r.modulos[0].module_code == "DASHBOARD"


def test_token_response_rechaza_permisos_legacy() -> None:
    with pytest.raises(ValidationError):
        TokenResponse(
            access_token="x", uid=1, username="a", email="a@b.co",
            roles=[], modulos=[], permisos=["FOO"],  # type: ignore[call-arg]
        )


# ── MeResponse ──────────────────────────────────────────────────────────────

def test_me_response_no_tiene_campo_permisos() -> None:
    assert "permisos" not in MeResponse.model_fields


def test_me_response_tiene_campos_self_y_modulos() -> None:
    campos = set(MeResponse.model_fields.keys())
    esperados = {"uid", "username", "email", "roles", "tiene_incentivos", "programa", "modulos"}
    assert esperados.issubset(campos)


def test_me_response_construye_minimo() -> None:
    r = MeResponse(
        uid=1, username="x", email="x@y.co",
        roles=["comisionista"], tiene_incentivos=False, programa=1, modulos=[],
    )
    assert r.programa == 1
    assert r.modulos == []


# ── CambioPasswordRequest — política de longitud AP-0044 ────────────────────

def test_cambio_password_exige_12_caracteres_usuario_final() -> None:
    """AP-0044: la nueva contraseña debe tener al menos 12 caracteres."""
    assert PASSWORD_MIN_LONGITUD_USUARIO_FINAL == 12
    # Corta pero con complejidad válida: aísla el fallo a la longitud.
    corta: str = "Abc1!def"  # 8 caracteres, 4 tipos
    with pytest.raises(ValidationError):
        CambioPasswordRequest(
            password_actual="actual", nueva_password=corta, confirmar_password=corta
        )


def test_cambio_password_acepta_12_caracteres() -> None:
    req = CambioPasswordRequest(
        password_actual="x", nueva_password=PASSWORD_VALIDA, confirmar_password=PASSWORD_VALIDA
    )
    assert req.nueva_password == PASSWORD_VALIDA


def test_cambio_password_actual_no_aplica_politica_de_longitud() -> None:
    """password_actual valida con min_length=1: puede ser una clave legacy corta."""
    req = CambioPasswordRequest(
        password_actual="x", nueva_password=PASSWORD_VALIDA, confirmar_password=PASSWORD_VALIDA
    )
    assert req.password_actual == "x"


# ── CambioPasswordRequest — complejidad AP-0051 ─────────────────────────────

def test_contar_tipos_caracter_distingue_los_cuatro_tipos() -> None:
    assert PASSWORD_MIN_TIPOS_CARACTER == 3
    assert contar_tipos_caracter("Abcdefghij1!") == 4   # min+may+dig+esp
    assert contar_tipos_caracter("abcdefghij12") == 2   # min+dig
    assert contar_tipos_caracter("abcdefghijkl") == 1   # solo min
    assert contar_tipos_caracter("Abcdefghij12") == 3   # min+may+dig


def test_cambio_password_rechaza_complejidad_insuficiente() -> None:
    """AP-0051: 12 caracteres pero solo 2 tipos (minúscula + dígito) → rechazada."""
    debil: str = "abcdefghij12"
    assert len(debil) >= PASSWORD_MIN_LONGITUD_USUARIO_FINAL
    with pytest.raises(ValidationError):
        CambioPasswordRequest(
            password_actual="x", nueva_password=debil, confirmar_password=debil
        )


def test_cambio_password_acepta_tres_de_cuatro_tipos() -> None:
    """AP-0051: 3 de 4 tipos (minúscula + mayúscula + dígito, sin especial) → aceptada."""
    tres_tipos: str = "Abcdefghij12"
    assert contar_tipos_caracter(tres_tipos) == PASSWORD_MIN_TIPOS_CARACTER
    req = CambioPasswordRequest(
        password_actual="x", nueva_password=tres_tipos, confirmar_password=tres_tipos
    )
    assert req.nueva_password == tres_tipos
