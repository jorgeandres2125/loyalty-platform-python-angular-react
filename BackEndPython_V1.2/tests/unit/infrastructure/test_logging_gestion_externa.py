"""Pruebas de conformidad AP-0027: la app no gestiona sus propios logs.

La gestión de logs (rotación, almacenamiento, envío) la realiza el SO/Docker,
no la aplicación. Estos tests verifican que `configurar_logging()` instala solo
un StreamHandler (salida al stream del proceso) y nunca un FileHandler.
"""
from __future__ import annotations

import logging
import sys

import pytest

from src.infrastructure.config.logging_config import configurar_logging


@pytest.fixture(autouse=True)
def _restaurar_root_logger() -> object:
    """Guarda y restaura el estado del root logger entre tests."""
    root = logging.getLogger()
    handlers_previos = root.handlers[:]
    filters_previos = root.filters[:]
    level_previo = root.level
    yield
    root.handlers = handlers_previos
    root.filters = filters_previos
    root.level = level_previo


def test_no_instala_file_handler() -> None:
    """AP-0027: la app no escribe logs a ficheros propios."""
    configurar_logging()
    root = logging.getLogger()
    file_handlers = [h for h in root.handlers if isinstance(h, logging.FileHandler)]
    assert not file_handlers, (
        "Se encontró un FileHandler — la app NO debe gestionar sus propios logs"
    )


def test_instala_exactamente_un_stream_handler() -> None:
    """AP-0027: el único handler es StreamHandler (stream del proceso → SO)."""
    configurar_logging()
    root = logging.getLogger()
    assert len(root.handlers) == 1
    assert isinstance(root.handlers[0], logging.StreamHandler)
    assert not isinstance(root.handlers[0], logging.FileHandler)


def test_stream_handler_escribe_a_stderr_o_stdout() -> None:
    """AP-0027: el stream es stderr o stdout (capturado por Docker/SO), no un fichero."""
    configurar_logging()
    root = logging.getLogger()
    handler = root.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    stream = handler.stream
    assert stream in (sys.stdout, sys.stderr), (
        f"El StreamHandler apunta a {stream!r}, no a stdout/stderr"
    )


def test_formato_json_preserva_estructura_para_colector() -> None:
    """AP-0027: los logs en modo json son parseable por colectores externos."""
    import json

    configurar_logging(formato="json")
    root = logging.getLogger()
    handler = root.handlers[0]

    import io
    buffer = io.StringIO()
    handler.stream = buffer

    logging.getLogger("sufi.test_ap0027").info("mensaje de prueba")
    salida = buffer.getvalue().strip()

    parsed: dict = json.loads(salida)
    assert "timestamp" in parsed
    assert "level" in parsed
    assert "message" in parsed


def test_llamadas_sucesivas_no_acumulan_handlers() -> None:
    """AP-0027: re-invocar configurar_logging() no duplica handlers."""
    configurar_logging()
    configurar_logging()
    root = logging.getLogger()
    stream_handlers = [h for h in root.handlers if isinstance(h, logging.StreamHandler)]
    assert len(stream_handlers) == 1, (
        f"Se acumularon {len(stream_handlers)} handlers tras dos llamadas"
    )
