from __future__ import annotations

import asyncio
import datetime as dt
import re
import secrets
from typing import Any, Final

import httpx

from src.shared.constants.email_gateway import (
    EMAIL_AUTH_PATH,
    EMAIL_SEND_PATH,
    TOKEN_MARGEN_EXPIRACION_SEG,
)


class CadenaEmailNotifier:
    """Notificador vía gateway HTTP 'email-send-on-demand' (Cadena/Axces).

    Implementa `NotificadorCorreo` (PEP 544) — reutilizable por cualquier caso de
    uso que dependa del puerto, no solo AP-0004. El envío es de dos pasos:

    1. `POST {base}/management/api/v1/auth/login` con usuario/clave → `authToken`
       (JWT). El token se cachea en memoria hasta poco antes de su expiración
       (`expiresIn`); el login se reintenta bajo un `asyncio.Lock` para no abrir
       varias sesiones en paralelo.
    2. `POST {base}/email-send-on-demand//api/v1/email/send` con
       `Authorization: Bearer <token>`. Si responde 401 (token invalidado en el
       servidor), se invalida el token local, se re-loguea y se reintenta una vez.

    El cuerpo HTML llega ya renderizado (con el nombre incluido), así que
    `messageFields` va vacío; no se usa la plantilla `%nombre%` del gateway.
    """

    _REGEX_FRACCION: Final[re.Pattern[str]] = re.compile(r"^(.*\.\d{6})\d*(.*)$")

    def __init__(
        self,
        base_url: str,
        usuario: str,
        password: str,
        customer: str,
        product: str,
        channel: str,
        remitente: str,
        validar_lista_negra: bool,
        timeout: int,
        verificar_tls: bool = True,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        base: str = base_url.strip()
        if "://" not in base:
            base = f"https://{base}"
        self._base_url: str = base.rstrip("/")
        self._usuario: str = usuario
        self._password: str = password
        self._customer: str = customer
        self._product: str = product
        self._channel: str = channel
        self._remitente: str = remitente
        self._validar_lista_negra: bool = validar_lista_negra
        self._timeout: int = timeout
        self._verificar_tls: bool = verificar_tls
        self._transport: httpx.AsyncBaseTransport | None = transport
        self._token: str | None = None
        self._token_expira: dt.datetime | None = None
        self._lock: asyncio.Lock = asyncio.Lock()

    async def enviar_async(
        self,
        destinatario: str,
        asunto: str,
        cuerpo_texto: str,
        cuerpo_html: str,
    ) -> None:
        async with self._abrir_cliente() as cliente:
            token: str = await self._obtener_token(cliente)
            respuesta: httpx.Response = await self._enviar(
                cliente, token, destinatario, asunto, cuerpo_html
            )
            if self._es_no_autorizado(respuesta):
                self._invalidar_token()
                token = await self._obtener_token(cliente)
                respuesta = await self._enviar(
                    cliente, token, destinatario, asunto, cuerpo_html
                )
            self._verificar_exito(respuesta)

    async def enviar_masivo_async(
        self,
        destinatarios: list[str],
        asunto: str,
        cuerpo_texto: str,
        cuerpo_html: str,
    ) -> None:
        # AP-0088: el gateway no expone un campo Bcc; para no revelar la lista
        # de destinatarios se envia una peticion por destinatario (cada uno se
        # ve solo a si mismo). Se reutiliza el cliente y el token en el lote.
        if not destinatarios:
            return
        async with self._abrir_cliente() as cliente:
            for destinatario in destinatarios:
                token: str = await self._obtener_token(cliente)
                respuesta: httpx.Response = await self._enviar(
                    cliente, token, destinatario, asunto, cuerpo_html
                )
                if self._es_no_autorizado(respuesta):
                    self._invalidar_token()
                    token = await self._obtener_token(cliente)
                    respuesta = await self._enviar(
                        cliente, token, destinatario, asunto, cuerpo_html
                    )
                self._verificar_exito(respuesta)

    def _abrir_cliente(self) -> httpx.AsyncClient:
        # Con transport inyectado (tests) `verify` se ignora; en producción controla
        # la validación del certificado TLS del gateway.
        if self._transport is not None:
            return httpx.AsyncClient(timeout=self._timeout, transport=self._transport)
        return httpx.AsyncClient(timeout=self._timeout, verify=self._verificar_tls)

    # ── Token ──────────────────────────────────────────────────────────────────

    async def _obtener_token(self, cliente: httpx.AsyncClient) -> str:
        async with self._lock:
            if self._token is not None and not self._token_por_vencer():
                return self._token
            respuesta: httpx.Response = await cliente.post(
                self._url(EMAIL_AUTH_PATH),
                json={"username": self._usuario, "password": self._password},
            )
            respuesta.raise_for_status()
            datos: dict[str, Any] = respuesta.json()
            token: str | None = datos.get("authToken")
            if not token:
                raise RuntimeError("El login del gateway de correo no devolvió 'authToken'.")
            self._token = token
            self._token_expira = self._parsear_expiracion(datos.get("expiresIn"))
            return token

    def _invalidar_token(self) -> None:
        self._token = None
        self._token_expira = None

    def _token_por_vencer(self) -> bool:
        if self._token_expira is None:
            return True
        ahora: dt.datetime = dt.datetime.now(dt.UTC)
        margen: dt.timedelta = dt.timedelta(seconds=TOKEN_MARGEN_EXPIRACION_SEG)
        return ahora >= (self._token_expira - margen)

    @classmethod
    def _parsear_expiracion(cls, valor: str | None) -> dt.datetime | None:
        if not valor:
            return None
        # fromisoformat no admite >6 dígitos de fracción; 'Z' se normaliza a offset.
        texto: str = valor.strip().replace("Z", "+00:00")
        emparejado: re.Match[str] | None = cls._REGEX_FRACCION.match(texto)
        if emparejado is not None:
            texto = emparejado.group(1) + emparejado.group(2)
        try:
            momento: dt.datetime = dt.datetime.fromisoformat(texto)
        except ValueError:
            return None
        if momento.tzinfo is None:
            momento = momento.replace(tzinfo=dt.UTC)
        return momento

    # ── Envío ──────────────────────────────────────────────────────────────────

    async def _enviar(
        self,
        cliente: httpx.AsyncClient,
        token: str,
        destinatario: str,
        asunto: str,
        cuerpo_html: str,
    ) -> httpx.Response:
        cuerpo: dict[str, Any] = {
            "customer": self._customer,
            "product": self._product,
            "channel": self._channel,
            "validateBlackList": self._validar_lista_negra,
            "clientMailingId": self._generar_mailing_id(),
            "clientMessageId": self._generar_message_id(),
            "emailInfo": {
                "subject": asunto,
                "sender": self._remitente,
                "mask": asunto,
                "recipient": destinatario,
                "htmlbody": cuerpo_html,
                "messageFields": [],
            },
        }
        return await cliente.post(
            self._url(EMAIL_SEND_PATH),
            json=cuerpo,
            headers={"Authorization": f"Bearer {token}"},
        )

    # ── Helpers ──────────────────────────────────────────────────────────────────

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    @staticmethod
    def _es_no_autorizado(respuesta: httpx.Response) -> bool:
        if respuesta.status_code == httpx.codes.UNAUTHORIZED:
            return True
        try:
            return int(respuesta.json().get("status", 0)) == 401
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _verificar_exito(respuesta: httpx.Response) -> None:
        respuesta.raise_for_status()
        try:
            cuerpo: dict[str, Any] = respuesta.json()
        except ValueError:
            return
        estado: Any = cuerpo.get("status")
        if estado is not None and int(estado) >= 400:
            raise RuntimeError(
                f"El gateway de correo rechazó el envío: {cuerpo.get('message')}"
            )

    @staticmethod
    def _generar_mailing_id() -> str:
        # Formato del contrato: yymmdd (p.ej. 230330).
        return dt.datetime.now(dt.UTC).strftime("%y%m%d")

    @staticmethod
    def _generar_message_id() -> str:
        marca: str = dt.datetime.now(dt.UTC).strftime("%Y%m%d%H%M%S")
        return f"sufi-{marca}-{secrets.token_hex(4)}"
