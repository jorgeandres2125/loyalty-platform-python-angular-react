from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.infrastructure.security.verificador_integridad_archivos import (
    VerificadorIntegridadArchivos,
)


def _sha256(datos: bytes) -> str:
    return "sha256:" + hashlib.sha256(datos).hexdigest()


def _preparar(tmp_path: Path, contenido: bytes) -> tuple[str, str]:
    archivo: Path = tmp_path / "critico.txt"
    archivo.write_bytes(contenido)
    baseline: dict[str, str] = {"critico.txt": _sha256(contenido)}
    baseline_path: Path = tmp_path / "baseline.json"
    baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
    return str(baseline_path), str(tmp_path)


def test_sin_baseline_no_disponible() -> None:
    verificador = VerificadorIntegridadArchivos("", "/app")
    assert verificador.baseline_disponible() is False
    assert verificador.verificar() == []


def test_integridad_ok_sin_desviaciones(tmp_path: Path) -> None:
    baseline_path, base_dir = _preparar(tmp_path, b"contenido original")
    verificador = VerificadorIntegridadArchivos(baseline_path, base_dir)
    assert verificador.baseline_disponible() is True
    assert verificador.verificar() == []


def test_modificacion_detectada(tmp_path: Path) -> None:
    baseline_path, base_dir = _preparar(tmp_path, b"contenido original")
    (tmp_path / "critico.txt").write_bytes(b"contenido alterado")
    verificador = VerificadorIntegridadArchivos(baseline_path, base_dir)
    desviaciones = verificador.verificar()
    assert len(desviaciones) == 1
    assert desviaciones[0].ruta == "critico.txt"
    assert desviaciones[0].tipo == "modificacion"


def test_archivo_ausente_detectado(tmp_path: Path) -> None:
    baseline_path, base_dir = _preparar(tmp_path, b"contenido original")
    (tmp_path / "critico.txt").unlink()
    verificador = VerificadorIntegridadArchivos(baseline_path, base_dir)
    desviaciones = verificador.verificar()
    assert len(desviaciones) == 1
    assert desviaciones[0].tipo == "ausente"
