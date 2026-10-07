from __future__ import annotations

from typing import Protocol


class NotificadorCorreo(Protocol):
    """Puerto de salida para enviar correo.

    Abstracción reutilizable por cualquier caso de uso (no solo AP-0004).
    Implementaciones: gateway HTTP 'email-send-on-demand' (CadenaEmailNotifier),
    SMTP real (SmtpEmailNotifier) y consola/log (ConsoleEmailNotifier, desarrollo
    cuando no hay gateway ni SMTP configurados).
    """

    async def enviar_async(
        self,
        destinatario: str,
        asunto: str,
        cuerpo_texto: str,
        cuerpo_html: str,
    ) -> None: ...

    async def enviar_masivo_async(
        self,
        destinatarios: list[str],
        asunto: str,
        cuerpo_texto: str,
        cuerpo_html: str,
    ) -> None:
        """Envio MASIVO: los destinatarios deben ir ocultos entre si (BCC o CCO).

        AP-0088: ninguna implementacion debe exponer la lista de destinatarios
        a los demas (ni en To ni en Cc). El SMTP usa el encabezado Bcc; el
        gateway HTTP, que no expone un campo Bcc, envia una peticion por
        destinatario (cada uno se ve solo a si mismo).
        """
        ...
