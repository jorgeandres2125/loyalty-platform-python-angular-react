from __future__ import annotations

import logging

from src.application.services.servicio_alerta_seguridad import ServicioAlertaSeguridad
from src.domain.entities.alerta_seguridad import AlertaSeguridad
from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.shared.constants.alertas import PREFIJO_EVENTO_ALERTA


def alerta_desde_record(record: logging.LogRecord) -> AlertaSeguridad | None:
    # AP-0134: deriva una AlertaSeguridad de un registro del logger sufi.seguridad. Los
    # eventos propios del alertador (prefijo alerta_) se ignoran para evitar recursion.
    evento: object = getattr(record, "evento_seguridad", None)
    if not isinstance(evento, str) or evento.startswith(PREFIJO_EVENTO_ALERTA):
        return None
    sev_raw: object = getattr(record, "severidad", None)
    if not isinstance(sev_raw, str):
        return None
    try:
        severidad: SeveridadSeguridad = SeveridadSeguridad(sev_raw)
    except ValueError:
        return None
    actor: str = str(
        getattr(record, "actor", "") or getattr(record, "usuario", "") or "desconocido"
    )
    ip: str = str(getattr(record, "ip", "") or getattr(record, "ip_publica", "") or "")
    corr: str = str(
        getattr(record, "evento_id", "") or getattr(record, "correlation_id", "") or ""
    )
    detalle_raw: object = getattr(record, "detalle", None)
    return AlertaSeguridad(
        titulo="[" + severidad.value.upper() + "] " + evento,
        severidad=severidad,
        evento=evento,
        resultado=str(getattr(record, "resultado", "")),
        actor=actor,
        ip=ip,
        correlation_id=corr,
        detalle=detalle_raw if isinstance(detalle_raw, str) else None,
    )


class AlertaHandler(logging.Handler):
    """AP-0134: handler enganchado al logger sufi.seguridad. Por cada evento cuya
    severidad alcance el umbral, deriva una AlertaSeguridad y la entrega al servicio de
    alertamiento. Fail-safe: un error aqui nunca interrumpe el logging."""

    def __init__(self, servicio: ServicioAlertaSeguridad) -> None:
        super().__init__()
        self._servicio: ServicioAlertaSeguridad = servicio

    def emit(self, record: logging.LogRecord) -> None:
        try:
            alerta: AlertaSeguridad | None = alerta_desde_record(record)
            if alerta is not None:
                self._servicio.procesar(alerta)
        except Exception:
            self.handleError(record)
