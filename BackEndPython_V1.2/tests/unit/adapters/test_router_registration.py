"""Tests de configuración: confirma que las rutas críticas están registradas.

No requiere BD ni invocar lifespan: solo inspecciona `app.routes`.
"""
from __future__ import annotations

import pytest

from src.adapters.api.main import app


def _paths() -> set[str]:
    return {r.path for r in app.routes if hasattr(r, "path")}


def test_health_endpoint_registrado() -> None:
    assert "/health" in _paths()


def test_auth_endpoints_registrados() -> None:
    paths = _paths()
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/auth/me" in paths
    assert "/api/v1/auth/password" in paths


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/me/perfil-contacto",
        "/api/v1/me/perfil-tributario",
        "/api/v1/me/perfil-emocional",
        "/api/v1/me/dashboard",
        "/api/v1/me/documentos",
        "/api/v1/me/documentos/upload",
        "/api/v1/me/documentos/{did}",
    ],
)
def test_me_endpoint_registrado(path: str) -> None:
    assert path in _paths(), f"falta endpoint {path}"


def test_endpoints_principales_de_otros_routers() -> None:
    paths = _paths()
    assert "/api/v1/dashboard/stats" in paths
    assert "/api/v1/sapin/token" in paths or any("/sapin" in p for p in paths)
    assert any("/api/v1/asesor-consumo" in p for p in paths)
    assert any("/api/v1/asesor-movilidad" in p for p in paths)


def test_endpoints_gestion_cuentas_ap0001_registrados() -> None:
    """AP-0001: panel admin + acción reutilizada en pantallas de asesor."""
    paths = _paths()
    assert "/api/v1/admin/usuarios" in paths
    assert "/api/v1/admin/usuarios/{uid}/estado" in paths
    assert "/api/v1/asesor-consumo/{numero_documento}/estado" in paths
    assert "/api/v1/asesor-movilidad/{numero_documento}/estado" in paths
