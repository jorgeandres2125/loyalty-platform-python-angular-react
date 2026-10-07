from __future__ import annotations

import logging

from src.domain.ports.outbound.sellador_log import SelladorLog
from src.domain.value_objects.eslabon_cadena import EslabonCadena
from src.shared.constants.cadena_log import (
    CAMPO_CADENA_ID,
    CAMPO_HASH_ACTUAL,
    CAMPO_HASH_CONTENIDO,
    CAMPO_HASH_PREVIO,
    CAMPO_SECUENCIA,
    PREFIJO_LOGGER_SELLADO,
    SEPARADOR_CONTENIDO,
)


class SelladorLogFilter(logging.Filter):
    """AP-0025: sella cada evento de auditoria con un eslabon de la cadena de hash.

    Se adjunta al handler despues de la redaccion (AP-0087) y del contexto de
    correlacion (AP-0024), de modo que el contenido sellado es el definitivo ya
    redactado. Solo sella los eventos del logger de seguridad (prefijo configurable);
    el resto pasa sin sellar. A cada evento sellado le adjunta los campos del sello
    (secuencia, hash previo, hash del contenido y hash del eslabon), que el formateador
    emite junto al registro para que el destino inmutable (SIEM y WORM) los conserve.
    """

    def __init__(self, sellador: SelladorLog, prefijo: str = PREFIJO_LOGGER_SELLADO) -> None:
        super().__init__()
        self._sellador: SelladorLog = sellador
        self._prefijo: str = prefijo

    def filter(self, record: logging.LogRecord) -> bool:
        if not record.name.startswith(self._prefijo):
            return True
        contenido: str = self._contenido_canonico(record)
        eslabon: EslabonCadena = self._sellador.sellar(contenido)
        setattr(record, CAMPO_CADENA_ID, getattr(self._sellador, "cadena_id", ""))
        setattr(record, CAMPO_SECUENCIA, eslabon.secuencia)
        setattr(record, CAMPO_HASH_PREVIO, eslabon.hash_previo)
        setattr(record, CAMPO_HASH_CONTENIDO, eslabon.hash_contenido)
        setattr(record, CAMPO_HASH_ACTUAL, eslabon.hash_actual)
        return True

    @staticmethod
    def _contenido_canonico(record: logging.LogRecord) -> str:
        partes: list[str] = [
            record.name,
            record.levelname,
            record.getMessage(),
            str(getattr(record, "evento_id", "")),
            str(getattr(record, "usuario", "")),
            str(getattr(record, "severidad", "")),
        ]
        return SEPARADOR_CONTENIDO.join(partes)
