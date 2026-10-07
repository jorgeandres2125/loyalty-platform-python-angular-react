from __future__ import annotations

import logging


class ConsoleEmailNotifier:
    """Notificador de desarrollo: no envía correo real, registra el mensaje (con el
    código OTP que viaja en él) en el log estructurado.

    Se activa cuando no hay SMTP configurado (`smtp_host` vacío), igual que el
    patrón de crypto deshabilitada. Implementa `NotificadorCorreo` (PEP 544).
    """

    def __init__(self) -> None:
        self._log: logging.Logger = logging.getLogger("sufi.email")

    async def enviar_async(
        self,
        destinatario: str,
        asunto: str,
        cuerpo_texto: str,
        cuerpo_html: str,
    ) -> None:
        self._log.info(
            "correo_simulado (SMTP no configurado) — destinatario=%s asunto=%s\n%s",
            destinatario,
            asunto,
            cuerpo_texto,
        )

    async def enviar_masivo_async(
        self,
        destinatarios: list[str],
        asunto: str,
        cuerpo_texto: str,
        cuerpo_html: str,
    ) -> None:
        # AP-0088: en consola no se envia; se registra solo el conteo, sin
        # exponer la lista. En produccion el envio real va por Bcc (SMTP) o
        # por destinatario (gateway).
        self._log.info(
            "correo_masivo_simulado (BCC) destinatarios=%d asunto=%s",
            len(destinatarios),
            asunto,
        )
