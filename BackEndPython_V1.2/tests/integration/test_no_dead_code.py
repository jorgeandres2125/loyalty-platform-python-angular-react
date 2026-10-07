"""AP-0110: no debe haber codigo muerto (funciones/metodos/clases sin invocar).

Ejecuta vulture con la config de pyproject (src + vulture_whitelist.py). Si aparece
un simbolo no usado que no este justificado en el whitelist, vulture sale != 0 y la
prueba falla, forzando a eliminarlo o documentarlo.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

if importlib.util.find_spec("vulture") is None:  # pragma: no cover
    pytest.skip("vulture no instalado", allow_module_level=True)

_ROOT: Path = Path(__file__).resolve().parents[2]


def test_sin_codigo_muerto() -> None:
    resultado = subprocess.run(
        [sys.executable, "-m", "vulture"],
        cwd=_ROOT,
        capture_output=True,
        text=True,
    )
    assert resultado.returncode == 0, (
        "vulture detecto codigo muerto no justificado (AP-0110). "
        "Eliminelo o agreguelo a vulture_whitelist.py con justificacion:\n"
        + resultado.stdout
        + resultado.stderr
    )
