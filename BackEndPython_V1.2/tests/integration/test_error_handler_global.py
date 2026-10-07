"""AP-0119: la app no revela stack traces, SQL ni nombres de tablas o BD.

Una excepcion no controlada (incluido un error tipo driver con SQL y tablas)
produce un 500 con mensaje generico; el cuerpo nunca contiene traceback, SQL ni
identificadores internos.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.error_handlers import unhandled_exception_handler

SL = chr(47)
_TABLA = "users_perfil_contacto"
_TABLA2 = "users_migracion"


def _make_client() -> TestClient:
    app = FastAPI()
    app.add_exception_handler(Exception, unhandled_exception_handler)

    async def boom() -> dict:
        raise RuntimeError("fallo con SELECT secret FROM " + _TABLA)

    async def sql_error() -> dict:
        raise Exception(
            "(pyodbc.ProgrammingError) columna numero_documento invalida en " + _TABLA2
        )

    app.add_api_route(SL + "boom", boom)
    app.add_api_route(SL + "sql", sql_error)
    return TestClient(app, raise_server_exceptions=False)


_CLIENT = _make_client()


def test_500_respuesta_generica() -> None:
    r = _CLIENT.get(SL + "boom")
    assert r.status_code == 500
    assert r.json() == {"detail": "Error interno del servidor."}


def test_500_no_filtra_traceback_ni_sql() -> None:
    cuerpo = _CLIENT.get(SL + "boom").text
    assert "Traceback" not in cuerpo
    assert "SELECT" not in cuerpo
    assert _TABLA not in cuerpo
    assert "RuntimeError" not in cuerpo


def test_500_no_filtra_sql_de_driver_ni_tablas() -> None:
    cuerpo = _CLIENT.get(SL + "sql").text
    assert _TABLA2 not in cuerpo
    assert "pyodbc" not in cuerpo
    assert "numero_documento" not in cuerpo


def test_app_real_registra_handler_global() -> None:
    from src.adapters.api.main import create_app
    from src.infrastructure.config.settings import Settings

    app = create_app(
        Settings(
            app_env="production",
            debug=False,
            jwt_secret_key="xxxxxxxxxxxxxxxxxxxxxxxx",
            db_password="xxxxxxxxxxxxxxxxxxxxxxxx",
            db_user="app_sufi",
            smtp_password="",
            email_api_password="",
            kms_provider="aws",
            kms_key_id="kms-test-key-id",
        )
    )
    assert Exception in app.exception_handlers
