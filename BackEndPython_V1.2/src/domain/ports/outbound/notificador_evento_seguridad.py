from __future__ import annotations

from typing import Protocol

from src.domain.entities.alerta_seguridad import AlertaSeguridad


class NotificadorEventoSeguridad(Protocol):
    """AP-0134: puerto de salida para emitir una alerta de seguridad a un canal (correo,
    webhook de Microsoft Teams o Slack, o log). El ServicioAlertaSeguridad captura los
    errores de cada canal, de modo que un canal caido no interrumpe a los demas ni a la
    peticion en curso."""

    async def alertar(self, alerta: AlertaSeguridad) -> None: ...
