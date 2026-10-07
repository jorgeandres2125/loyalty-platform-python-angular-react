from __future__ import annotations

from typing import Final

TIPOS_DOCUMENTO_NOMBRES: Final[dict[int, str]] = {
    4: "Cédula",
    5: "RUT",
    6: "Contrato",
    7: "EPS",
    8: "AFP / Pensiones (obligatoria)",
    9: "ARL",
    10: "Medicina Prepagada",
    11: "Certificado intereses de vivienda",
    12: "Pensión Voluntaria",
    13: "AFC",
    14: "Dependientes",
}

TIPOS_DOCUMENTO_PREFIJOS: Final[dict[int, str]] = {
    4: "CC",
    5: "RUT",
    6: "CONTRATO",
    7: "EPS",
    8: "AFP",
    9: "ARL",
    10: "PREPAGADA",
    11: "VIVIENDA",
    12: "PENSIONVOL",
    13: "AFC",
    14: "DEPENDIENTES",
}

ESTADOS_DOCUMENTO_VALIDOS: Final[frozenset[str]] = frozenset({
    "pendiente",
    "revision",
    "aprobado",
})
