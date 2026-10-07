from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from src.application.services.servicio_verificacion_integridad import (
    ServicioVerificacionIntegridad,
)
from src.infrastructure.security.verificador_integridad_archivos import (
    VerificadorIntegridadArchivos,
)


def _sha256(datos: bytes) -> str:
    return "sha256:" + hashlib.sha256(datos).hexdigest()


def _servicio(
    tmp_path: Path, contenido_actual: bytes, habilitado: bool
) -> ServicioVerificacionIntegridad:
    archivo: Path = tmp_path / "critico.txt"
    archivo.write_bytes(contenido_actual)
    baseline: dict[str, str] = {"critico.txt": _sha256(b"original")}
    baseline_path: Path = tmp_path / "baseline.json"
    baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
    verificador = VerificadorIntegridadArchivos(str(baseline_path), str(tmp_path))
    return ServicioVerificacionIntegridad(verificador, habilitado)


def test_deshabilitado_no_registra(tmp_path: Path, caplog) -> None:
    servicio = _servicio(tmp_path, b"original", habilitado=False)
    with caplog.at_level(logging.INFO, logger="sufi.seguridad"):
        servicio.ejecutar()
    assert caplog.records == []


def test_integridad_ok_registra_evento_exito(tmp_path: Path, caplog) -> None:
    servicio = _servicio(tmp_path, b"original", habilitado=True)
    with caplog.at_level(logging.INFO, logger="sufi.seguridad"):
        servicio.ejecutar()
    eventos = [
        r for r in caplog.records
        if getattr(r, "evento_seguridad", "") == "integridad_archivo"
    ]
    assert len(eventos) == 1
    assert eventos[0].resultado == "exito"


def test_cambio_detectado_registra_alerta(tmp_path: Path, caplog) -> None:
    servicio = _servicio(tmp_path, b"alterado", habilitado=True)
    with caplog.at_level(logging.INFO, logger="sufi.seguridad"):
        servicio.ejecutar()
    alertas = [r for r in caplog.records if getattr(r, "resultado", "") == "fallo"]
    assert len(alertas) == 1
    assert alertas[0].archivo == "critico.txt"
    assert alertas[0].cambio == "modificacion"
