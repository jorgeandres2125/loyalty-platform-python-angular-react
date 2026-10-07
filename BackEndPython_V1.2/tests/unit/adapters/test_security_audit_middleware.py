"""Tests para SecurityAuditMiddleware (auditoría de acceso por petición — AP-0022)."""
from __future__ import annotations

import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.middleware.security_audit_middleware import SecurityAuditMiddleware
from src.infrastructure.config.settings import Settings
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD


def _app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(SecurityAuditMiddleware, settings=Settings())

    @app.get("/ok")
    def ok() -> dict[str, bool]:
        return {"ok": True}

    @app.get("/api/v1/reportes/algo")
    def confidencial() -> dict[str, int]:
        return {"x": 1}

    @app.get("/boom")
    def boom() -> dict[str, bool]:
        raise RuntimeError("boom")

    return app


def _eventos(caplog: pytest.LogCaptureFixture) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.name == LOGGER_SEGURIDAD]


def test_acceso_exitoso_se_registra_info(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    resp = TestClient(_app()).get("/ok")
    assert resp.status_code == 200
    recs = _eventos(caplog)
    assert any(r.evento_seguridad == "acceso" and r.resultado == "exito" for r in recs)


def test_ruta_confidencial_se_marca(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    TestClient(_app()).get("/api/v1/reportes/algo")
    recs = _eventos(caplog)
    assert any(r.evento_seguridad == "acceso_confidencial" and r.confidencial for r in recs)


def test_excepcion_no_controlada_se_registra_error(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    resp = TestClient(_app(), raise_server_exceptions=False).get("/boom")
    assert resp.status_code == 500
    recs = _eventos(caplog)
    hubo_excepcional: bool = any(
        r.evento_seguridad == "evento_excepcional" and r.levelno == logging.ERROR for r in recs
    )
    assert hubo_excepcional
