"""Tests para CadenaEmailNotifier (gateway HTTP de correo de dos pasos).

Se usa httpx.MockTransport para interceptar login y send sin red real.
asyncio_mode = "auto" → no hace falta marcar las pruebas async.
"""
from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest

from src.infrastructure.external.cadena_email_notifier import CadenaEmailNotifier

_FUTURO: str = "2999-01-01T00:00:00.000000Z"
_PASADO: str = "2000-01-01T00:00:00.000000Z"


def _make_notifier(
    handler: Callable[[httpx.Request], httpx.Response],
    **overrides: Any,
) -> CadenaEmailNotifier:
    params: dict[str, Any] = {
        "base_url": "https://gw.example.com",
        "usuario": "AdminUser",
        "password": "1234567",
        "customer": "CX",
        "product": "email",
        "channel": "email-channel-soketlabs",
        "remitente": "no-responder@suficontigo.com",
        "validar_lista_negra": False,
        "timeout": 10,
        "transport": httpx.MockTransport(handler),
    }
    params.update(overrides)
    return CadenaEmailNotifier(**params)


async def test_login_y_envio_cachea_token() -> None:
    llamadas: dict[str, int] = {"login": 0, "send": 0}
    capturado: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if "login" in request.url.path:
            llamadas["login"] += 1
            return httpx.Response(200, json={"authToken": "TOK1", "expiresIn": _FUTURO})
        llamadas["send"] += 1
        capturado["auth"] = request.headers.get("Authorization")
        capturado["body"] = json.loads(request.content)
        capturado["path"] = request.url.path
        return httpx.Response(200, json={"status": 200, "message": "Succesfully", "errors": []})

    notifier: CadenaEmailNotifier = _make_notifier(handler)
    await notifier.enviar_async("dest@x.com", "Asunto", "texto", "<p>hola</p>")
    await notifier.enviar_async("dest2@x.com", "Asunto2", "texto2", "<p>hola2</p>")

    assert llamadas["login"] == 1  # token cacheado entre envíos
    assert llamadas["send"] == 2
    assert capturado["auth"] == "Bearer TOK1"
    assert capturado["path"] == "/email-send-on-demand//api/v1/email/send"
    body: dict[str, Any] = capturado["body"]
    assert body["customer"] == "CX"
    assert body["emailInfo"]["recipient"] == "dest2@x.com"
    assert body["emailInfo"]["subject"] == "Asunto2"
    assert body["emailInfo"]["mask"] == "Asunto2"
    assert body["emailInfo"]["htmlbody"] == "<p>hola2</p>"
    assert body["emailInfo"]["messageFields"] == []


async def test_reintento_tras_401_reloguea() -> None:
    estado: dict[str, int] = {"login": 0, "send": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if "login" in request.url.path:
            estado["login"] += 1
            return httpx.Response(
                200, json={"authToken": f"TOK{estado['login']}", "expiresIn": _FUTURO}
            )
        estado["send"] += 1
        if estado["send"] == 1:
            return httpx.Response(401, json={"status": 401, "message": "Unauthorized"})
        return httpx.Response(200, json={"status": 200, "message": "Succesfully", "errors": []})

    notifier: CadenaEmailNotifier = _make_notifier(handler)
    await notifier.enviar_async("d@x.com", "A", "t", "<p>h</p>")

    assert estado["login"] == 2  # login inicial + re-login tras 401
    assert estado["send"] == 2


async def test_token_expirado_se_renueva() -> None:
    estado: dict[str, int] = {"login": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if "login" in request.url.path:
            estado["login"] += 1
            return httpx.Response(200, json={"authToken": "T", "expiresIn": _PASADO})
        return httpx.Response(200, json={"status": 200})

    notifier: CadenaEmailNotifier = _make_notifier(handler)
    await notifier.enviar_async("d@x.com", "A", "t", "<p>h</p>")
    await notifier.enviar_async("d@x.com", "A", "t", "<p>h</p>")

    assert estado["login"] == 2  # token ya vencido → re-login en cada envío


async def test_falla_si_gateway_rechaza_envio() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "login" in request.url.path:
            return httpx.Response(200, json={"authToken": "T", "expiresIn": _FUTURO})
        return httpx.Response(200, json={"status": 500, "message": "Boom", "errors": ["x"]})

    notifier: CadenaEmailNotifier = _make_notifier(handler)
    with pytest.raises(RuntimeError, match="rechazó"):
        await notifier.enviar_async("d@x.com", "A", "t", "<p>h</p>")


def test_parsear_expiracion_admite_nanosegundos_y_z() -> None:
    momento = CadenaEmailNotifier._parsear_expiracion("2026-06-16T21:41:24.6286961Z")
    assert momento is not None
    assert momento.year == 2026
    assert momento.tzinfo is not None


def test_parsear_expiracion_invalida_devuelve_none() -> None:
    assert CadenaEmailNotifier._parsear_expiracion("no-es-fecha") is None
    assert CadenaEmailNotifier._parsear_expiracion(None) is None


async def test_masivo_una_peticion_por_destinatario() -> None:
    recipients: list[str] = []
    sends: dict[str, int] = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if "login" in request.url.path:
            return httpx.Response(200, json={"authToken": "T", "expiresIn": _FUTURO})
        sends["n"] += 1
        cuerpo: dict[str, Any] = json.loads(request.content)
        recipients.append(cuerpo["emailInfo"]["recipient"])
        return httpx.Response(200, json={"status": 200})

    notif: CadenaEmailNotifier = _make_notifier(handler)
    await notif.enviar_masivo_async(["a@x.com", "b@x.com", "c@x.com"], "A", "t", "h")
    assert sends["n"] == 3
    assert recipients == ["a@x.com", "b@x.com", "c@x.com"]
