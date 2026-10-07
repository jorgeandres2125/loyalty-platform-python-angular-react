from __future__ import annotations

from src.domain.value_objects.resultado_retencion import ResultadoRetencion
from src.domain.value_objects.retencion_categoria import RetencionCategoria
from src.shared.constants.retencion_log import (
    NIVELES_ERROR,
    PREFIJO_ADMIN,
    PREFIJO_AUDITORIA,
    PREFIJO_SEGURIDAD,
)


class ClasificadorRetencion:
    """AP-0026: clasifica cada log en una categoria de retencion y resuelve su plazo.

    La categoria se deriva del logger y del nivel: los eventos de seguridad y auditoria
    se conservan mas tiempo que los de operacion o error. El plazo en dias por categoria
    es configurable por entorno, de modo que la politica regulatoria vigente se ajuste sin
    tocar el codigo.
    """

    def __init__(self, dias_por_categoria: dict[RetencionCategoria, int]) -> None:
        self._dias: dict[RetencionCategoria, int] = dict(dias_por_categoria)

    @property
    def dias_por_categoria(self) -> dict[RetencionCategoria, int]:
        return dict(self._dias)

    def clasificar(self, logger_name: str, nivel: str) -> ResultadoRetencion:
        categoria: RetencionCategoria = self._categoria(logger_name, nivel)
        dias: int = self._dias.get(categoria, 0)
        return ResultadoRetencion(categoria=categoria, dias=dias)

    @staticmethod
    def _categoria(logger_name: str, nivel: str) -> RetencionCategoria:
        if logger_name.startswith(PREFIJO_SEGURIDAD):
            return RetencionCategoria.SEGURIDAD
        if logger_name.startswith(PREFIJO_AUDITORIA):
            return RetencionCategoria.AUDITORIA
        if logger_name.startswith(PREFIJO_ADMIN):
            return RetencionCategoria.ADMINISTRACION
        if nivel in NIVELES_ERROR:
            return RetencionCategoria.ERROR
        return RetencionCategoria.OPERACION
