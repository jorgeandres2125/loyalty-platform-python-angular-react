from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Final

from src.domain.value_objects.desviacion_integridad import DesviacionIntegridad

_TIPO_MODIFICACION: Final[str] = "modificacion"
_TIPO_AUSENTE: Final[str] = "ausente"
_TAMANO_BLOQUE: Final[int] = 65536


class VerificadorIntegridadArchivos:
    """AP-0120: verifica la integridad de los archivos criticos de la aplicacion comparando su
    hash SHA-256 actual contra una linea base (baseline) generada en el pipeline y embebida en
    la imagen. Devuelve la lista de desviaciones (vacia si todo coincide). No lanza si el
    baseline no esta configurado: la verificacion es opcional y fail-safe.
    """

    def __init__(self, baseline_path: str, base_dir: str) -> None:
        self._baseline_path: str = baseline_path
        self._base_dir: Path = Path(base_dir)

    def baseline_disponible(self) -> bool:
        return bool(self._baseline_path) and Path(self._baseline_path).is_file()

    def _cargar_baseline(self) -> dict[str, str]:
        with open(self._baseline_path, encoding="utf-8") as fh:
            datos: dict[str, str] = json.load(fh)
        return datos

    @staticmethod
    def _hash_archivo(ruta: Path) -> str:
        hasher = hashlib.sha256()
        with open(ruta, "rb") as fh:
            for bloque in iter(lambda: fh.read(_TAMANO_BLOQUE), b""):
                hasher.update(bloque)
        return "sha256:" + hasher.hexdigest()

    def verificar(self) -> list[DesviacionIntegridad]:
        if not self.baseline_disponible():
            return []
        baseline: dict[str, str] = self._cargar_baseline()
        desviaciones: list[DesviacionIntegridad] = []
        for ruta_rel, hash_esperado in baseline.items():
            ruta_abs: Path = self._base_dir / ruta_rel
            if not ruta_abs.is_file():
                desviaciones.append(
                    DesviacionIntegridad(
                        ruta=ruta_rel,
                        tipo=_TIPO_AUSENTE,
                        hash_baseline=hash_esperado,
                        hash_actual="",
                    )
                )
                continue
            hash_actual: str = self._hash_archivo(ruta_abs)
            if hash_actual != hash_esperado:
                desviaciones.append(
                    DesviacionIntegridad(
                        ruta=ruta_rel,
                        tipo=_TIPO_MODIFICACION,
                        hash_baseline=hash_esperado,
                        hash_actual=hash_actual,
                    )
                )
        return desviaciones
