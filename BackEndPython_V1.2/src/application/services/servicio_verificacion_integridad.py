from __future__ import annotations

import logging

from src.domain.value_objects.desviacion_integridad import DesviacionIntegridad
from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.infrastructure.security.verificador_integridad_archivos import (
    VerificadorIntegridadArchivos,
)
from src.shared.constants.eventos_seguridad import (
    EVENTO_INTEGRIDAD_ARCHIVO,
    LOGGER_SEGURIDAD,
    RESULTADO_EXITO,
    RESULTADO_FALLO,
)

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)


class ServicioVerificacionIntegridad:
    """AP-0120: ejecuta la verificacion de integridad de los archivos criticos de la app y la
    reporta en bitacora (logger de seguridad sufi punto seguridad), reutilizando la severidad
    (AP-0023), la cadena tamper-evident (AP-0025) y el gateway de logs (AP-0027). Fail-safe:
    nunca interrumpe el arranque; si no hay baseline, no hace nada."""

    def __init__(
        self, verificador: VerificadorIntegridadArchivos, habilitado: bool
    ) -> None:
        self._verificador: VerificadorIntegridadArchivos = verificador
        self._habilitado: bool = habilitado

    def _campos(self, resultado: str, severidad: SeveridadSeguridad) -> dict[str, object]:
        return {
            "evento_seguridad": EVENTO_INTEGRIDAD_ARCHIVO,
            "severidad": severidad.value,
            "resultado": resultado,
        }

    def ejecutar(self) -> None:
        if not self._habilitado or not self._verificador.baseline_disponible():
            return
        try:
            desviaciones: list[DesviacionIntegridad] = self._verificador.verificar()
        except OSError:
            _logger.warning(
                "AP-0120: no se pudo verificar la integridad de archivos criticos",
                extra=self._campos(RESULTADO_FALLO, SeveridadSeguridad.MEDIA),
            )
            return
        if not desviaciones:
            _logger.info(
                "AP-0120: integridad de archivos criticos verificada OK",
                extra=self._campos(RESULTADO_EXITO, SeveridadSeguridad.INFORMATIVA),
            )
            return
        for desviacion in desviaciones:
            campos: dict[str, object] = self._campos(
                RESULTADO_FALLO, SeveridadSeguridad.ALTA
            )
            campos["archivo"] = desviacion.ruta
            campos["cambio"] = desviacion.tipo
            campos["hash_baseline"] = desviacion.hash_baseline
            campos["hash_actual"] = desviacion.hash_actual
            _logger.warning(
                "AP-0120: cambio de integridad detectado en archivo critico",
                extra=campos,
            )
