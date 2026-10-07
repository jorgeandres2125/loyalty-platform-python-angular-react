from __future__ import annotations

import logging

from src.domain.entities.alerta_seguridad import AlertaSeguridad
from src.shared.constants.alertas import EVENTO_ALERTA_CANAL_LOG
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)


class NotificadorLogAlerta:
    """AP-0134: canal de alerta por defecto (siempre disponible, sin dependencias
    externas). Escribe la alerta en el log de seguridad; util en desarrollo y como
    respaldo cuando no hay correo ni webhook. El pipeline SIEM la recoge del stream."""

    async def alertar(self, alerta: AlertaSeguridad) -> None:
        _logger.warning(
            "ALERTA %s actor=%s corr=%s",
            alerta.titulo,
            alerta.actor,
            alerta.correlation_id,
            extra={
                "evento_seguridad": EVENTO_ALERTA_CANAL_LOG,
                "severidad": alerta.severidad.value,
                "resultado": "exito",
                "actor": alerta.actor,
                "correlation_id": alerta.correlation_id,
            },
        )
