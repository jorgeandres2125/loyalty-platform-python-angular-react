from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import time
from collections.abc import Callable
from typing import Final

from src.application.dto.resultado_desafio_otp_dto import ResultadoDesafioOtpDTO
from src.domain.entities.desafio_otp_login import DesafioOtpLogin
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.otp_invalido import OtpInvalido
from src.domain.ports.outbound.desafio_otp_store import DesafioOtpStore
from src.domain.ports.outbound.notificador_correo import NotificadorCorreo
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD
from src.shared.constants.otp_login import (
    EVENTO_OTP_LOGIN,
    OTP_LOGIN_ASUNTO,
    OTP_LOGIN_CODIGO_LONGITUD,
)

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)
_NL: Final[str] = chr(10)


class ServicioOtpLogin:
    """AP-0012: segundo factor OTP de un solo uso en el proceso de autenticacion (login).

    Para los usuarios criticos (roles configurables), tras validar la contrasena se emite
    un codigo OTP al correo de la cuenta y el login no entrega token hasta verificarlo. El
    codigo es de un solo uso (se elimina del almacen al verificarlo con exito), con TTL e
    intentos limitados. Reutiliza el patron OTP de AP-0004 y AP-0005. Deshabilitado o para
    usuarios no criticos, requiere_otp devuelve False y el login se comporta como antes.
    """

    def __init__(
        self,
        desafio_store: DesafioOtpStore,
        notificador: NotificadorCorreo,
        roles_criticos: frozenset[str],
        max_intentos: int,
        ttl_segundos: int,
        enabled: bool,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._desafio_store: DesafioOtpStore = desafio_store
        self._notificador: NotificadorCorreo = notificador
        self._roles_criticos: frozenset[str] = roles_criticos
        self._max_intentos: int = max_intentos
        self._ttl_segundos: int = ttl_segundos
        self._enabled: bool = enabled
        self._clock: Callable[[], float] = clock

    def requiere_otp(self, usuario: UsuarioEntity) -> bool:
        if not self._enabled or not usuario.email:
            return False
        return any(rol.value in self._roles_criticos for rol in usuario.roles)

    async def emitir_desafio_async(self, usuario: UsuarioEntity) -> ResultadoDesafioOtpDTO:
        codigo: str = self._generar_codigo()
        desafio_id: str = secrets.token_urlsafe(18)
        desafio: DesafioOtpLogin = DesafioOtpLogin(
            desafio_id=desafio_id,
            uid=usuario.uid or 0,
            codigo_hash=self._hash(codigo),
            intentos_restantes=self._max_intentos,
            creado_en_monotonic=self._clock(),
        )
        await self._desafio_store.guardar(desafio_id, desafio)
        texto: str
        html: str
        texto, html = self._construir_mensaje(codigo, usuario.nombre)
        await self._notificador.enviar_async(
            destinatario=usuario.email,
            asunto=OTP_LOGIN_ASUNTO,
            cuerpo_texto=texto,
            cuerpo_html=html,
        )
        _logger.info(
            "OTP de login emitido uid=%s",
            usuario.uid,
            extra=self._campos("exito", str(usuario.uid)),
        )
        return ResultadoDesafioOtpDTO(
            desafio_id=desafio_id,
            email_enmascarado=self._enmascarar(usuario.email),
            expira_en_segundos=self._ttl_segundos,
        )

    async def verificar_async(self, desafio_id: str, codigo: str) -> int:
        desafio: DesafioOtpLogin | None = await self._desafio_store.obtener(desafio_id)
        if desafio is None:
            raise OtpInvalido("El codigo expiro o no existe. Inicia sesion de nuevo.")
        if hmac.compare_digest(desafio.codigo_hash, self._hash(codigo)):
            await self._desafio_store.eliminar(desafio_id)
            _logger.info(
                "OTP de login verificado uid=%s",
                desafio.uid,
                extra=self._campos("exito", str(desafio.uid)),
            )
            return desafio.uid
        restantes: int = desafio.intentos_restantes - 1
        if restantes <= 0:
            await self._desafio_store.eliminar(desafio_id)
            _logger.warning(
                "OTP de login bloqueado por intentos uid=%s",
                desafio.uid,
                extra=self._campos("fallo", str(desafio.uid)),
            )
            raise OtpInvalido(
                "Codigo incorrecto. Se agotaron los intentos; inicia sesion de nuevo.",
                intentos_restantes=0,
            )
        await self._desafio_store.guardar(desafio_id, desafio.con_intento_consumido())
        raise OtpInvalido("Codigo incorrecto.", intentos_restantes=restantes)

    # -- Helpers --
    @staticmethod
    def _campos(resultado: str, actor: str) -> dict[str, object]:
        return {
            "evento_seguridad": EVENTO_OTP_LOGIN,
            "resultado": resultado,
            "actor": actor,
        }

    @staticmethod
    def _generar_codigo() -> str:
        maximo: int = 10**OTP_LOGIN_CODIGO_LONGITUD
        return str(secrets.randbelow(maximo)).zfill(OTP_LOGIN_CODIGO_LONGITUD)

    @staticmethod
    def _hash(codigo: str) -> str:
        return hashlib.sha256(codigo.encode("utf-8")).hexdigest()

    @staticmethod
    def _enmascarar(email: str) -> str:
        local: str
        dominio: str
        try:
            local, dominio = email.split("@", 1)
        except ValueError:
            return "***"
        visible: str = local[0] if local else "*"
        return visible + "***@" + dominio

    @staticmethod
    def _construir_mensaje(codigo: str, nombre: str) -> tuple[str, str]:
        saludo: str = ("Hola, " + nombre + ":") if nombre else "Hola:"
        lineas: list[str] = [
            saludo,
            "",
            "Tu codigo de acceso de un solo uso es:",
            "",
            codigo,
            "",
            "Ingresalo para completar tu inicio de sesion. Vence en pocos minutos y solo "
            "sirve una vez. Si no intentaste iniciar sesion, cambia tu contrasena.",
            "",
            "SUFI",
            "Siempre a tu lado.",
        ]
        texto: str = _NL.join(lineas)
        html: str = (
            "<p>" + saludo + "</p>"
            "<p>Tu codigo de acceso de un solo uso es:</p>"
            '<p style="font-size:24px;font-weight:bold;letter-spacing:3px">' + codigo + "</p>"
            "<p>Ingresalo para completar tu inicio de sesion. Vence en pocos minutos y solo "
            "sirve una vez. Si no intentaste iniciar sesion, cambia tu contrasena.</p>"
            "<p>SUFI<br>Siempre a tu lado.</p>"
        )
        return texto, html
