"""AP-0118: rutas de carga implicita endurecidas en la imagen Docker.

Valida los invariantes del Dockerfile del backend: PATH solo con directorios de
sistema (sin rutas de usuario ni el directorio actual), PYTHONSAFEPATH activo,
usuario sin privilegios y CMD por ruta absoluta de confianza.
"""
from __future__ import annotations

from pathlib import Path

import pytest

SL = chr(47)
_DOCKERFILE = Path(__file__).resolve().parents[3].joinpath("Docker", "Dockerfile.backend")

if not _DOCKERFILE.is_file():
    pytest.skip("Dockerfile.backend no disponible", allow_module_level=True)

_TXT = _DOCKERFILE.read_text(encoding="utf-8")
_U = SL + "usr" + SL + "local"
_SYS = (
    _U + SL + "sbin:" + _U + SL + "bin:" + SL + "usr" + SL + "sbin:"
    + SL + "usr" + SL + "bin:" + SL + "sbin:" + SL + "bin"
)


def _linea_path() -> str:
    for ln in _TXT.splitlines():
        if ln.startswith("ENV PATH="):
            return ln
    return ""


def test_path_solo_directorios_de_sistema() -> None:
    assert 'ENV PATH="' + _SYS + '"' in _TXT


def test_path_no_antepone_rutas_de_usuario() -> None:
    linea = _linea_path()
    assert linea != ""
    assert SL + "app" not in linea
    assert SL + "home" not in linea


def test_pythonsafepath_activo() -> None:
    assert "PYTHONSAFEPATH=1" in _TXT


def test_usuario_sin_privilegios() -> None:
    assert "USER appuser" in _TXT
    assert "USER root" not in _TXT


def test_cmd_usa_ruta_absoluta_de_confianza() -> None:
    binario = chr(34) + _U + SL + "bin" + SL + "uvicorn" + chr(34)
    assert binario in _TXT
    assert chr(34) + "uvicorn" + chr(34) + "," not in _TXT
