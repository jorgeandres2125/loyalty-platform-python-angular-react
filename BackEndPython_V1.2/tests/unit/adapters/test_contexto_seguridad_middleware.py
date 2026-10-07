"""Tests para ContextoSeguridadMiddleware (correlación por petición — AP-0024)."""
from __future__ import annotations

import logging
import re

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.middleware.contexto_seguridad_middleware import (
    ContextoSeguridadMiddleware,
)
from src.infrastructure.config.settings import Settings
from src.infrastructure.logging.contexto_seguridad_filter import ContextoSeguridadFilter
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD

_UUID4_RE: re.Pattern[str] = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def _app_con_spy() -> tuple[FastAPI, list[logging.LogRecord]]:
    """App mínima con ContextoSeguridadMiddleware + un handler que captura registros."""
    app = FastAPI()
    app.add_middleware(ContextoSeguridadMiddleware, settings=Settings())

    registros: list[logging.LogRecord] = []

    class _Spy(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            registros.append(record)

    spy = _Spy()
    spy.addFilter(ContextoSeguridadFilter())
    logging.getLogger(LOGGER_SEGURIDAD).addHandler(spy)
    logging.getLogger(LOGGER_SEGURIDAD).setLevel(logging.DEBUG)

    @app.get("/ping")
    def ping() -> dict[str, str]:
        logging.getLogger(LOGGER_SEGURIDAD).info("pong")
        return {"pong": "ok"}

    return app, registros


def test_middleware_inyecta_evento_id_uuid4(caplog: pytest.LogCaptureFixture) -> None:
    app, registros = _app_con_spy()
    TestClient(app).get("/ping")
    assert registros, "El handler espía no capturó ningún registro"
    rec = registros[-1]
    evento_id: str = str(getattr(rec, "evento_id", ""))
    assert _UUID4_RE.match(evento_id), f"evento_id no es UUID4: {evento_id!r}"


def test_middleware_inyecta_metodo_y_ruta() -> None:
    app, registros = _app_con_spy()
    TestClient(app).get("/ping")
    rec = registros[-1]
    assert getattr(rec, "metodo", None) == "GET"
    assert getattr(rec, "ruta", None) == "/ping"


def test_middleware_inyecta_ip_local_e_ip_publica() -> None:
    app, registros = _app_con_spy()
    TestClient(app).get("/ping")
    rec = registros[-1]
    assert getattr(rec, "ip_local", None) is not None
    assert getattr(rec, "ip_publica", None) is not None


def test_middleware_inyecta_usuario_anonimo_sin_token() -> None:
    app, registros = _app_con_spy()
    TestClient(app).get("/ping")
    rec = registros[-1]
    assert getattr(rec, "usuario", None) == "anonimo"


def test_middleware_evento_id_distinto_por_peticion() -> None:
    app, registros = _app_con_spy()
    client = TestClient(app)
    client.get("/ping")
    client.get("/ping")
    assert len(registros) >= 2
    ids: list[str] = [str(getattr(r, "evento_id", "")) for r in registros]
    assert ids[0] != ids[1], "evento_id debe ser único por petición"
