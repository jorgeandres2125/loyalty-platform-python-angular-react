from __future__ import annotations

from enum import StrEnum


class RetencionCategoria(StrEnum):
    """AP-0026: categoria de retencion de un log, que determina su plazo de conservacion.

    Cada evento se clasifica en una categoria; la infraestructura materializa el plazo
    (dias) de cada categoria en niveles de almacenamiento (hot, warm y cold WORM). Los
    plazos concretos son configurables por entorno segun la politica regulatoria vigente.
    """

    SEGURIDAD = "seguridad"
    AUDITORIA = "auditoria"
    ADMINISTRACION = "administracion"
    OPERACION = "operacion"
    ERROR = "error"
