from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoDispositivoDTO:
    """AP-0014: resultado de registrar el acceso desde un dispositivo."""

    device_hash: str
    es_nuevo: bool
    device_name: str
