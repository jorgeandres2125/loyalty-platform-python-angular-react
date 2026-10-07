from __future__ import annotations

from typing import Final

PERFIL_CONSUMO: Final[str] = "0"
PERFIL_VEHICULO: Final[str] = "1"
PERFIL_AMBOS: Final[str] = "2"

PERFILES_EJECUTIVO_NOMBRES: Final[dict[str, str]] = {
    PERFIL_CONSUMO: "Ejecutivo Consumo",
    PERFIL_VEHICULO: "Ejecutivo Vehiculo",
    PERFIL_AMBOS: "Ejecutivo Movilidad. Consumo y Servicios",
}

PERFILES_EJECUTIVO_VALIDOS: Final[frozenset[str]] = frozenset(PERFILES_EJECUTIVO_NOMBRES.keys())

TIPOS_DOCUMENTO_EJECUTIVO: Final[frozenset[str]] = frozenset(
    {"CC", "CE", "F&I", "GC", "PEP", "PPT", "VDA"}
)
