"""Tests para ContextoSeguridadFilter y JSONFormatter timestamp (AP-0024)."""
from __future__ import annotations

import json
import logging

from src.infrastructure.config.logging_config import JSONFormatter
from src.infrastructure.logging.contexto_seguridad import ContextoSeguridad
from src.infrastructure.logging.contexto_seguridad_filter import ContextoSeguridadFilter


def _make_record() -> logging.LogRecord:
    return logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="hola", args=(), exc_info=None,
    )


# ── ContextoSeguridadFilter ──────────────────────────────────────────────────


def test_filter_inyecta_campos_del_contexto() -> None:
    filtro = ContextoSeguridadFilter()
    token = ContextoSeguridad.establecer({"evento_id": "abc-123", "usuario": "jdoe"})
    try:
        record = _make_record()
        filtro.filter(record)
        assert record.evento_id == "abc-123"  # type: ignore[attr-defined]
        assert record.usuario == "jdoe"  # type: ignore[attr-defined]
    finally:
        ContextoSeguridad.limpiar(token)


def test_filter_no_sobrescribe_atributos_existentes() -> None:
    filtro = ContextoSeguridadFilter()
    token = ContextoSeguridad.establecer({"usuario": "del_contexto"})
    try:
        record = _make_record()
        record.usuario = "ya_estaba"  # type: ignore[attr-defined]
        filtro.filter(record)
        assert record.usuario == "ya_estaba"  # type: ignore[attr-defined]
    finally:
        ContextoSeguridad.limpiar(token)


def test_filter_contexto_vacio_no_falla() -> None:
    filtro = ContextoSeguridadFilter()
    record = _make_record()
    assert filtro.filter(record) is True


def test_filter_retorna_true_siempre() -> None:
    filtro = ContextoSeguridadFilter()
    token = ContextoSeguridad.establecer({"evento_id": "x", "ruta": "/api/v1/me"})
    try:
        assert filtro.filter(_make_record()) is True
    finally:
        ContextoSeguridad.limpiar(token)


def test_filter_inyecta_todos_los_campos_de_correlacion() -> None:
    filtro = ContextoSeguridadFilter()
    campos: dict[str, object] = {
        "evento_id": "uuid-1",
        "usuario": "42",
        "ip_local": "127.0.0.1",
        "ip_publica": "203.0.113.5",
        "metodo": "POST",
        "ruta": "/api/v1/auth/login",
    }
    token = ContextoSeguridad.establecer(campos)
    try:
        record = _make_record()
        filtro.filter(record)
        for clave, valor in campos.items():
            assert getattr(record, clave) == valor
    finally:
        ContextoSeguridad.limpiar(token)


# ── JSONFormatter — timestamp con milisegundos (AP-0024) ────────────────────


def test_json_formatter_timestamp_incluye_milisegundos() -> None:
    formatter = JSONFormatter()
    record = _make_record()
    salida: dict[str, object] = json.loads(formatter.format(record))
    ts: str = str(salida["timestamp"])
    # ISO 8601 con ms: "2026-06-17T12:34:56.789+00:00"
    # La parte fraccionaria debe tener exactamente 3 dígitos antes del offset.
    assert "." in ts, f"Sin fracción de segundo en timestamp: {ts}"
    fraccion: str = ts.split(".")[1].split("+")[0].split("-")[0]
    assert len(fraccion) == 3, f"Se esperaban 3 dígitos de ms, se obtuvo: {fraccion!r}"


def test_json_formatter_timestamp_incluye_offset_utc() -> None:
    formatter = JSONFormatter()
    record = _make_record()
    salida: dict[str, object] = json.loads(formatter.format(record))
    ts: str = str(salida["timestamp"])
    assert "+00:00" in ts, f"Falta offset UTC en timestamp: {ts}"
