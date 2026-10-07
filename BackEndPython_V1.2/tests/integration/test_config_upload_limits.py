"""AP-0137: el limite de subida es configurable por entorno y consultable en la API."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.routers import config_router
from src.infrastructure.config.dependencies import get_settings
from src.infrastructure.config.settings import Settings

_RUTA = "/api/v1/config/uploads"


def _client(max_bytes: int) -> TestClient:
    app = FastAPI()
    app.include_router(config_router.router, prefix="/api/v1/config")
    app.dependency_overrides[get_settings] = lambda: Settings(max_upload_bytes=max_bytes)
    return TestClient(app)


def test_endpoint_expone_el_limite() -> None:
    r = _client(5_242_880).get(_RUTA)
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["max_upload_bytes"] == 5_242_880
    assert cuerpo["max_upload_mb"] == 5.0


def test_endpoint_refleja_valor_configurado() -> None:
    r = _client(10_485_760).get(_RUTA)
    assert r.json()["max_upload_bytes"] == 10_485_760
    assert r.json()["max_upload_mb"] == 10.0


def test_setting_se_lee_de_variable_de_entorno(monkeypatch) -> None:
    monkeypatch.setenv("MAX_UPLOAD_BYTES", "2097152")
    assert Settings().max_upload_bytes == 2_097_152


def test_endpoint_publico_en_app_real() -> None:
    from src.adapters.api.main import create_app

    app = create_app(Settings(app_env="development"))
    rutas = [getattr(r, "path", "") for r in app.routes]
    assert any("config" in ruta and "uploads" in ruta for ruta in rutas)
