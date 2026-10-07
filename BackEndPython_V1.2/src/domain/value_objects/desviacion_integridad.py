from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DesviacionIntegridad:
    """AP-0120: una desviacion detectada entre el estado actual de un archivo critico y su
    linea base (baseline) firmada. El tipo es modificacion (el hash cambio) o ausente (el
    archivo del baseline ya no existe)."""

    ruta: str
    tipo: str
    hash_baseline: str
    hash_actual: str
