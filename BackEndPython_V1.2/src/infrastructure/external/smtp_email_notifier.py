from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage


class SmtpEmailNotifier:
    """Notificador SMTP real (staging/producción). Implementa `NotificadorCorreo`.

    `smtplib` es bloqueante; el envío se delega a un executor para no bloquear el
    event loop de FastAPI.
    """

    def __init__(
        self,
        host: str,
        port: int,
        usuario: str,
        password: str,
        remitente: str,
        usar_starttls: bool,
        timeout: int,
    ) -> None:
        self._host: str = host
        self._port: int = port
        self._usuario: str = usuario
        self._password: str = password
        self._remitente: str = remitente
        self._usar_starttls: bool = usar_starttls
        self._timeout: int = timeout

    async def enviar_async(
        self,
        destinatario: str,
        asunto: str,
        cuerpo_texto: str,
        cuerpo_html: str,
    ) -> None:
        mensaje: EmailMessage = EmailMessage()
        mensaje["Subject"] = asunto
        mensaje["From"] = self._remitente
        mensaje["To"] = destinatario
        mensaje.set_content(cuerpo_texto)
        mensaje.add_alternative(cuerpo_html, subtype="html")
        await asyncio.get_running_loop().run_in_executor(None, self._enviar_sync, mensaje)

    async def enviar_masivo_async(
        self,
        destinatarios: list[str],
        asunto: str,
        cuerpo_texto: str,
        cuerpo_html: str,
    ) -> None:
        if not destinatarios:
            return
        mensaje: EmailMessage = self._construir_mensaje_masivo(
            destinatarios, asunto, cuerpo_texto, cuerpo_html
        )
        await asyncio.get_running_loop().run_in_executor(None, self._enviar_sync, mensaje)

    def _construir_mensaje_masivo(
        self,
        destinatarios: list[str],
        asunto: str,
        cuerpo_texto: str,
        cuerpo_html: str,
    ) -> EmailMessage:
        # AP-0088: destinatarios en Bcc (copia oculta). To lleva solo el
        # remitente; smtplib.send_message reparte a los Bcc y elimina el
        # encabezado Bcc antes de transmitir, de modo que nadie ve a los demas.
        mensaje: EmailMessage = EmailMessage()
        mensaje["Subject"] = asunto
        mensaje["From"] = self._remitente
        mensaje["To"] = self._remitente
        mensaje["Bcc"] = ", ".join(destinatarios)
        mensaje.set_content(cuerpo_texto)
        mensaje.add_alternative(cuerpo_html, subtype="html")
        return mensaje

    def _enviar_sync(self, mensaje: EmailMessage) -> None:
        with smtplib.SMTP(self._host, self._port, timeout=self._timeout) as smtp:
            if self._usar_starttls:
                smtp.starttls()
            if self._usuario:
                smtp.login(self._usuario, self._password)
            smtp.send_message(mensaje)
