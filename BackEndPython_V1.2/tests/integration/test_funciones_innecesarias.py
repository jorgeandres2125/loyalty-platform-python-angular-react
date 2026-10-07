"""AP-0116: funciones innecesarias deshabilitadas.

- Documentacion interactiva (docs, redoc, openapi) solo en development/test;
  en staging y produccion los endpoints quedan en None (404).
- Router de debug solo montado cuando debug=True (dev/test).
"""
from __future__ import annotations

from src.adapters.api.main import create_app
from src.infrastructure.config.settings import Settings

_STRONG = "xxxxxxxxxxxxxxxxxxxxxxxx"
SL = chr(47)


def _prod_settings() -> Settings:
    return Settings(
        app_env="production",
        debug=False,
        jwt_secret_key=_STRONG,
        db_password=_STRONG,
        db_user="app_sufi",
        smtp_password="",
        email_api_password="",
        kms_provider="aws",
        kms_key_id="kms-test-key-id",
    )


def test_docs_habilitados_property() -> None:
    assert Settings(app_env="development").docs_habilitados is True
    assert Settings(app_env="test").docs_habilitados is True
    assert _prod_settings().docs_habilitados is False
    staging = Settings(
        app_env="staging", jwt_secret_key=_STRONG, db_password=_STRONG, db_user="app_sufi", kms_provider="aws", kms_key_id="kms-test-key-id", email_api_password=_STRONG
    )
    assert staging.docs_habilitados is False


def test_docs_deshabilitados_en_produccion() -> None:
    app = create_app(_prod_settings())
    assert app.docs_url is None
    assert app.redoc_url is None
    assert app.openapi_url is None


def test_docs_habilitados_en_desarrollo() -> None:
    app = create_app(Settings(app_env="development"))
    assert app.docs_url == SL + "docs"
    assert app.redoc_url == SL + "redoc"
    assert app.openapi_url == SL + "openapi.json"


def test_debug_router_no_montado_en_produccion() -> None:
    app = create_app(_prod_settings())
    rutas = [getattr(r, "path", "") for r in app.routes]
    assert not any("debug" in ruta for ruta in rutas)


def test_debug_router_montado_en_desarrollo() -> None:
    app = create_app(Settings(app_env="development"))
    rutas = [getattr(r, "path", "") for r in app.routes]
    assert any("debug" in ruta for ruta in rutas)
