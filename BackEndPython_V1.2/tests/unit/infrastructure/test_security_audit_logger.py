"""Tests para SecurityAuditLogger (auditoría de eventos de seguridad — AP-0022)."""
from __future__ import annotations

import logging

import pytest

from src.infrastructure.logging.security_audit import SecurityAuditLogger
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD


def _ultimo(caplog: pytest.LogCaptureFixture) -> logging.LogRecord:
    registros = [r for r in caplog.records if r.name == LOGGER_SEGURIDAD]
    assert registros, "no se registró ningún evento de seguridad"
    return registros[-1]


def test_autenticacion_exito_es_info(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    SecurityAuditLogger().autenticacion(exito=True, actor="jdoe", ip="1.2.3.4")
    rec = _ultimo(caplog)
    assert rec.levelno == logging.INFO
    assert rec.evento_seguridad == "autenticacion"
    assert rec.resultado == "exito"
    assert rec.actor == "jdoe"
    assert rec.ip == "1.2.3.4"


def test_autenticacion_fallo_es_warning(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    SecurityAuditLogger().autenticacion(exito=False, actor="jdoe", ip="1.2.3.4")
    rec = _ultimo(caplog)
    assert rec.levelno == logging.WARNING
    assert rec.resultado == "fallo"


def test_cambio_credencial_fallo_es_warning(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    SecurityAuditLogger().cambio_credencial(exito=False, actor="7", ip="1.2.3.4")
    rec = _ultimo(caplog)
    assert rec.evento_seguridad == "cambio_credencial"
    assert rec.resultado == "fallo"
    assert rec.levelno == logging.WARNING


def test_acceso_http_2xx_es_info_exito(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    SecurityAuditLogger().acceso_http(
        metodo="GET", ruta="/api/v1/dashboard", status_code=200,
        ip="1.2.3.4", actor="7", duracion_ms=12, confidencial=False,
    )
    rec = _ultimo(caplog)
    assert rec.levelno == logging.INFO
    assert rec.evento_seguridad == "acceso"
    assert rec.resultado == "exito"
    assert rec.status_code == 200


def test_acceso_http_4xx_es_warning_fallo(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    SecurityAuditLogger().acceso_http(
        metodo="GET", ruta="/api/v1/me", status_code=403,
        ip="1.2.3.4", actor="7", duracion_ms=3, confidencial=False,
    )
    rec = _ultimo(caplog)
    assert rec.levelno == logging.WARNING
    assert rec.resultado == "fallo"


def test_acceso_http_confidencial_marca_evento(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    SecurityAuditLogger().acceso_http(
        metodo="GET", ruta="/api/v1/reportes/x", status_code=200,
        ip="1.2.3.4", actor="7", duracion_ms=5, confidencial=True,
    )
    rec = _ultimo(caplog)
    assert rec.evento_seguridad == "acceso_confidencial"
    assert rec.confidencial is True


def test_excepcional_es_error(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    SecurityAuditLogger().excepcional(ip="1.2.3.4", recurso="/x", detalle="RuntimeError: boom")
    rec = _ultimo(caplog)
    assert rec.levelno == logging.ERROR
    assert rec.evento_seguridad == "evento_excepcional"
    assert rec.resultado == "fallo"


# ── Severidad explícita por evento (AP-0023) ─────────────────────────────────


def test_autenticacion_exito_severidad_informativa(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    SecurityAuditLogger().autenticacion(exito=True, actor="jdoe", ip="1.2.3.4")
    assert _ultimo(caplog).severidad == "informativa"


def test_autenticacion_fallo_severidad_media(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    SecurityAuditLogger().autenticacion(exito=False, actor="jdoe", ip="1.2.3.4")
    assert _ultimo(caplog).severidad == "media"


def test_cambio_credencial_exito_severidad_baja(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    SecurityAuditLogger().cambio_credencial(exito=True, actor="7", ip="1.2.3.4")
    assert _ultimo(caplog).severidad == "baja"


def test_acceso_confidencial_severidad_baja(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    SecurityAuditLogger().acceso_http(
        metodo="GET", ruta="/api/v1/reportes/x", status_code=200,
        ip="1.2.3.4", actor="7", duracion_ms=5, confidencial=True,
    )
    assert _ultimo(caplog).severidad == "baja"


def test_acceso_5xx_severidad_alta(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    SecurityAuditLogger().acceso_http(
        metodo="GET", ruta="/api/v1/dashboard", status_code=500,
        ip="1.2.3.4", actor="7", duracion_ms=5, confidencial=False,
    )
    rec = _ultimo(caplog)
    assert rec.severidad == "alta"
    assert rec.levelno == logging.ERROR


def test_excepcional_severidad_alta(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    SecurityAuditLogger().excepcional(ip="1.2.3.4", recurso="/x", detalle="boom")
    assert _ultimo(caplog).severidad == "alta"


def test_todo_evento_lleva_severidad(caplog: pytest.LogCaptureFixture) -> None:
    """Garantía AP-0023: cada evento de seguridad registra su nivel de severidad."""
    caplog.set_level(logging.INFO, logger=LOGGER_SEGURIDAD)
    logger = SecurityAuditLogger()
    logger.autenticacion(exito=True, actor="a", ip="i")
    logger.cambio_credencial(exito=False, actor="a", ip="i")
    logger.acceso_http(
        metodo="GET", ruta="/x", status_code=200, ip="i", actor="a",
        duracion_ms=1, confidencial=False,
    )
    logger.excepcional(ip="i", recurso="/x", detalle="d")
    eventos = [r for r in caplog.records if r.name == LOGGER_SEGURIDAD]
    assert len(eventos) == 4
    assert all(getattr(r, "severidad", None) for r in eventos)
