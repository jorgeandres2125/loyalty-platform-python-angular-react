from __future__ import annotations

import logging

from src.domain.services.clasificador_retencion import ClasificadorRetencion
from src.domain.value_objects.resultado_retencion import ResultadoRetencion
from src.shared.constants.retencion_log import CAMPO_RETENCION_CATEGORIA, CAMPO_RETENCION_DIAS


class RetencionLogFilter(logging.Filter):
    """AP-0026: adjunta a cada log su categoria y plazo de retencion.

    Clasifica el registro (por logger y nivel) y agrega retencion_categoria y
    retencion_dias, para que el destino centralizado enrute cada evento a la tabla y al
    nivel de almacenamiento con el plazo correcto. La aplicacion solo declara la politica;
    la retencion efectiva la aplica la infraestructura.
    """

    def __init__(self, clasificador: ClasificadorRetencion) -> None:
        super().__init__()
        self._clasificador: ClasificadorRetencion = clasificador

    def filter(self, record: logging.LogRecord) -> bool:
        resultado: ResultadoRetencion = self._clasificador.clasificar(
            record.name, record.levelname
        )
        setattr(record, CAMPO_RETENCION_CATEGORIA, resultado.categoria.value)
        setattr(record, CAMPO_RETENCION_DIAS, resultado.dias)
        return True
