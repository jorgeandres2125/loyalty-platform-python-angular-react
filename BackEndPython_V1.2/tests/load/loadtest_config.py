"""Configuración central del arnés de carga (AP-0031 / AP-0032).

Todos los parámetros del SLO y de la siembra viven aquí para que la prueba sea
reproducible y auditable. Se pueden sobreescribir por variable de entorno sin
tocar código (clave para correr en distintos ambientes / CI).
"""
from __future__ import annotations

import os
from typing import Final

# ── Objetivo de concurrencia (decisión de negocio AP-0031/0032) ──────────────
# "Concurrencia máxima esperada" = 100 usuarios simultáneos en hora pico.
# Alineado con el pool de conexiones (db_pool_min + max_overflow = 100).
CONCURRENCIA_OBJETIVO: Final[int] = int(os.getenv("SUFI_LOAD_USERS", "100"))

# ── SLO — criterio de aceptación medible ─────────────────────────────────────
# AP-0031: tiempo de respuesta ≤ 5 s a concurrencia máxima → p95 < 5000 ms.
# AP-0032: 0 % de errores a concurrencia máxima → fail_ratio == 0.
SLO_P95_MS: Final[float] = float(os.getenv("SUFI_SLO_P95_MS", "5000"))
SLO_FAIL_RATIO: Final[float] = float(os.getenv("SUFI_SLO_FAIL_RATIO", "0.0"))

# ── Host objetivo ────────────────────────────────────────────────────────────
HOST: Final[str] = os.getenv("SUFI_LOAD_HOST", "http://127.0.0.1:8000")

# ── Usuarios sembrados para la prueba ────────────────────────────────────────
# numero_documento DEBE ser solo dígitos (validador del wizard) y name == doc.
# Rango reservado 9_900_000_xxx, muy por encima del max(uid)=15685 del snapshot,
# y reconocible para la limpieza (LIKE '99000000%').
LOADTEST_UID_BASE: Final[int] = 9_900_000          # uid = base + i
LOADTEST_DOC_BASE: Final[int] = 9_900_000_000      # numero_documento = base + i (10 dígitos)
LOADTEST_COUNT: Final[int] = int(os.getenv("SUFI_LOAD_SEED_COUNT", str(CONCURRENCIA_OBJETIVO)))
LOADTEST_PASSWORD: Final[str] = os.getenv("SUFI_LOAD_PASSWORD", "LoadTest2026*")
LOADTEST_DOC_PREFIJO: Final[str] = "99000000"      # para limpieza por LIKE

# ── Rol y catálogos válidos en el snapshot (verificados en sufiatulado) ──────
COMISIONISTA_RID: Final[int] = 4                    # dbo.role → 'comisionista'
DEPARTAMENTO_VALIDO: Final[str] = "5"              # dbo.departamentos.did existente
CIUDAD_VALIDA: Final[str] = "5001"                # dbo.ciudades.cid existente
PROGRAMA_MOVILIDAD: Final[int] = 1                 # comisionista_programa Movilidad


def uid_de_indice(i: int) -> int:
    """uid determinista del i-ésimo usuario de carga (1-based)."""
    return LOADTEST_UID_BASE + i


def documento_de_indice(i: int) -> str:
    """numero_documento (== username) determinista del i-ésimo usuario (1-based)."""
    return str(LOADTEST_DOC_BASE + i)
