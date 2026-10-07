"""E2E smoke tests.

Estos tests NO usan `with TestClient(app)` (que dispararía lifespan e intentaría
conectar a la BD). En su lugar instancian `TestClient(app)` directamente, lo cual
en Starlette 0.21+ omite el lifespan — suficiente para los chequeos puramente
de routing/auth abajo, que no tocan la sesión SQLAlchemy.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from src.adapters.api.main import app

_client: TestClient = TestClient(app, raise_server_exceptions=False)


def test_health_check_devuelve_200_y_status_ok() -> None:
    resp = _client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_me_dashboard_sin_token_devuelve_401() -> None:
    """RBAC: el endpoint /me/dashboard requiere Bearer token."""
    resp = _client.get("/api/v1/me/dashboard")
    assert resp.status_code == 401


def test_login_sin_credenciales_no_devuelve_200() -> None:
    """Sin body: debe rechazarse. 400/422 (Pydantic) o 500 (no init_db en este
    test smoke). Lo importante: nunca 200/2xx con credenciales vacías."""
    resp = _client.post("/api/v1/auth/login")
    assert resp.status_code >= 400


def test_endpoint_inexistente_devuelve_404() -> None:
    resp = _client.get("/api/v1/no-existe-este-endpoint")
    assert resp.status_code == 404
