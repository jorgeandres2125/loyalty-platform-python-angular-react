from __future__ import annotations

from typing import Final

# AP-0026: plazos de retencion por defecto (en dias), configurables por entorno. Los
# valores base reflejan requisitos regulatorios; el plazo regulatorio prevalece como piso.
DIAS_ANIO: Final[int] = 365
RETENCION_SEGURIDAD_DIAS_DEFECTO: Final[int] = 7 * DIAS_ANIO
RETENCION_AUDITORIA_DIAS_DEFECTO: Final[int] = 7 * DIAS_ANIO
RETENCION_ADMINISTRACION_DIAS_DEFECTO: Final[int] = 7 * DIAS_ANIO
RETENCION_OPERACION_DIAS_DEFECTO: Final[int] = 2 * DIAS_ANIO
RETENCION_ERROR_DIAS_DEFECTO: Final[int] = DIAS_ANIO

# Minimo regulatorio absoluto: ninguna categoria puede configurarse por debajo.
RETENCION_MINIMA_DIAS: Final[int] = 90

# Prefijos de logger que determinan la categoria y niveles considerados de error.
PREFIJO_SEGURIDAD: Final[str] = "sufi.seguridad"
PREFIJO_AUDITORIA: Final[str] = "sufi.auditoria"
PREFIJO_ADMIN: Final[str] = "sufi.admin"
NIVELES_ERROR: Final[frozenset[str]] = frozenset({"ERROR", "CRITICAL"})

# Campos que el filtro adjunta a cada LogRecord para el enrutado y ciclo de vida.
CAMPO_RETENCION_CATEGORIA: Final[str] = "retencion_categoria"
CAMPO_RETENCION_DIAS: Final[str] = "retencion_dias"

# Base regulatoria por categoria (clave = valor de RetencionCategoria) para la evidencia.
BASE_REGULATORIA: Final[dict[str, str]] = {
    "seguridad": "ISO 27001 A.5.28; Habeas Data Ley 1581; Superfinanciera",
    "auditoria": "ISO 27001 A.8.15; Ley 1581 de 2012",
    "administracion": "Separacion de funciones; no repudio",
    "operacion": "CIS Control 8.10; buenas practicas de observabilidad",
    "error": "Observabilidad y diagnostico",
}
