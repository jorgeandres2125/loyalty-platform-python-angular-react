from __future__ import annotations

import httpx

from src.domain.entities.alerta_seguridad import AlertaSeguridad

_TIMEOUT_DEFECTO: float = 5.0


class NotificadorWebhook:
    """AP-0134: canal de alerta por webhook entrante (Microsoft Teams o Slack). Envia un
    POST JSON con el resumen de la alerta. El ServicioAlertaSeguridad captura cualquier
    error de red, de modo que un webhook caido no interrumpe los demas canales."""

    def __init__(self, url: str, timeout: float = _TIMEOUT_DEFECTO) -> None:
        self._url: str = url
        self._timeout: float = timeout

    def payload(self, alerta: AlertaSeguridad) -> dict[str, object]:
        return {
            "text": alerta.titulo,
            "severidad": alerta.severidad.value,
            "evento": alerta.evento,
            "resultado": alerta.resultado,
            "actor": alerta.actor,
            "ip": alerta.ip,
            "correlation_id": alerta.correlation_id,
            "detalle": alerta.detalle or "",
        }

    async def alertar(self, alerta: AlertaSeguridad) -> None:
        async with httpx.AsyncClient(timeout=self._timeout) as cliente:
            respuesta: httpx.Response = await cliente.post(
                self._url, json=self.payload(alerta)
            )
            respuesta.raise_for_status()
