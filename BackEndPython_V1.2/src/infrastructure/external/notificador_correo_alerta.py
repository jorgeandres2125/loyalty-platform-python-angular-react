from __future__ import annotations

from src.domain.entities.alerta_seguridad import AlertaSeguridad
from src.domain.ports.outbound.notificador_correo import NotificadorCorreo


class NotificadorCorreoAlerta:
    """AP-0134: canal de alerta por correo. Reutiliza el puerto NotificadorCorreo
    (AP-0088) para enviar la alerta al buzon del equipo de seguridad. El cuerpo no
    incluye secretos: los campos del evento ya vienen redactados (AP-0087)."""

    def __init__(self, correo: NotificadorCorreo, destino: str) -> None:
        self._correo: NotificadorCorreo = correo
        self._destino: str = destino

    async def alertar(self, alerta: AlertaSeguridad) -> None:
        nl: str = chr(10)
        cuerpo: str = nl.join(
            [
                "Evento: " + alerta.evento,
                "Severidad: " + alerta.severidad.value,
                "Resultado: " + alerta.resultado,
                "Actor: " + alerta.actor,
                "IP: " + alerta.ip,
                "Correlacion: " + alerta.correlation_id,
                "Detalle: " + (alerta.detalle or ""),
            ]
        )
        html: str = "<pre>" + cuerpo + "</pre>"
        await self._correo.enviar_async(self._destino, alerta.titulo, cuerpo, html)
