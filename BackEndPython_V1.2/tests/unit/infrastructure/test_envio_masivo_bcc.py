"""AP-0088: el envio masivo oculta a los destinatarios (BCC o CCO)."""
from __future__ import annotations

import logging
from email.message import EmailMessage

import pytest

from src.application.use_cases.enviar_correo_masivo_use_case import EnviarCorreoMasivoUseCase
from src.infrastructure.external.console_email_notifier import ConsoleEmailNotifier
from src.infrastructure.external.smtp_email_notifier import SmtpEmailNotifier


def _smtp() -> SmtpEmailNotifier:
    return SmtpEmailNotifier(
        host="smtp.local",
        port=587,
        usuario="user",
        password="passlarga",
        remitente="no-responder@suficontigo.com",
        usar_starttls=True,
        timeout=10,
    )


def test_smtp_masivo_usa_bcc_y_no_expone_en_to_ni_cc() -> None:
    notif: SmtpEmailNotifier = _smtp()
    destinatarios: list[str] = ["a@x.com", "b@x.com", "c@x.com"]
    mensaje: EmailMessage = notif._construir_mensaje_masivo(
        destinatarios, "Asunto", "texto", "cuerpo-html"
    )
    bcc: str = str(mensaje["Bcc"])
    for correo in destinatarios:
        assert correo in bcc
    assert mensaje["To"] == "no-responder@suficontigo.com"
    assert mensaje["Cc"] is None
    for correo in destinatarios:
        assert correo not in str(mensaje["To"])


async def test_console_masivo_registra_conteo_sin_exponer_lista(
    caplog: pytest.LogCaptureFixture,
) -> None:
    notif: ConsoleEmailNotifier = ConsoleEmailNotifier()
    with caplog.at_level(logging.INFO, logger="sufi.email"):
        await notif.enviar_masivo_async(["a@x.com", "b@x.com"], "A", "t", "h")
    texto: str = caplog.text
    assert "masivo" in texto
    assert "a@x.com" not in texto


class _NotificadorFalso:
    def __init__(self) -> None:
        self.masivo: list[str] | None = None
        self.individuales: int = 0

    async def enviar_async(
        self,
        destinatario: str,
        asunto: str,
        cuerpo_texto: str,
        cuerpo_html: str,
    ) -> None:
        self.individuales += 1

    async def enviar_masivo_async(
        self,
        destinatarios: list[str],
        asunto: str,
        cuerpo_texto: str,
        cuerpo_html: str,
    ) -> None:
        self.masivo = list(destinatarios)


async def test_caso_uso_deduplica_y_usa_solo_envio_masivo() -> None:
    notif: _NotificadorFalso = _NotificadorFalso()
    uc: EnviarCorreoMasivoUseCase = EnviarCorreoMasivoUseCase(notificador=notif)
    enviados: int = await uc.ejecutar_async(
        ["a@x.com", "A@X.com", " b@x.com ", ""], "A", "t", "h"
    )
    assert enviados == 2
    assert notif.masivo == ["a@x.com", "b@x.com"]
    assert notif.individuales == 0


async def test_caso_uso_lista_vacia_no_envia() -> None:
    notif: _NotificadorFalso = _NotificadorFalso()
    uc: EnviarCorreoMasivoUseCase = EnviarCorreoMasivoUseCase(notificador=notif)
    enviados: int = await uc.ejecutar_async(["", "  "], "A", "t", "h")
    assert enviados == 0
    assert notif.masivo is None
