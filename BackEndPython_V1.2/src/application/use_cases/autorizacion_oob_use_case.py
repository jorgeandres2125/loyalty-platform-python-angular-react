from __future__ import annotations

import hashlib
import hmac
import json
import logging
import secrets
import time
from collections.abc import Callable
from typing import Final

from src.application.dto.resultado_iniciar_oob_dto import ResultadoIniciarOobDTO
from src.application.dto.resultado_resolver_oob_dto import ResultadoResolverOobDTO
from src.domain.entities.desafio_oob import DesafioOob
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.desafio_oob_invalido import DesafioOobInvalido
from src.domain.ports.outbound.desafio_oob_store import DesafioOobStore
from src.domain.ports.outbound.notificador_correo import NotificadorCorreo
from src.domain.ports.outbound.usuario_repository import UsuarioRepository
from src.domain.services.clasificador_criticidad import ClasificadorCriticidad
from src.domain.value_objects.canal_oob import CanalOob
from src.domain.value_objects.estado_desafio_oob import EstadoDesafioOob
from src.domain.value_objects.tipo_transaccion_critica import TipoTransaccionCritica
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD
from src.shared.constants.oob import (
    DESCRIPCION_TRANSACCION,
    EVENTO_OOB,
    OOB_ASUNTO,
    OOB_CODIGO_LONGITUD,
)

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)
_NL: Final[str] = chr(10)


class AutorizacionOobUseCase:
    """AP-0005: subsistema de confirmacion fuera de banda de transacciones criticas.

    `iniciar_async` clasifica la operacion (motor de riesgo MVP); si es critica genera
    un codigo OOB, crea un desafio PENDIENTE ligado al payload por su hash, lo guarda
    con TTL y lo envia por el canal (correo, reutilizando AP-0004). `resolver_async`
    aprueba (codigo correcto y vigente) o rechaza el desafio, con intentos limitados y
    un solo uso. Cada transicion se audita en el logger de seguridad (AP-0022).
    """

    def __init__(
        self,
        usuario_repo: UsuarioRepository,
        desafio_store: DesafioOobStore,
        notificador: NotificadorCorreo,
        clasificador: ClasificadorCriticidad,
        max_intentos: int,
        ttl_segundos: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._usuario_repo: UsuarioRepository = usuario_repo
        self._desafio_store: DesafioOobStore = desafio_store
        self._notificador: NotificadorCorreo = notificador
        self._clasificador: ClasificadorCriticidad = clasificador
        self._max_intentos: int = max_intentos
        self._ttl_segundos: int = ttl_segundos
        self._clock: Callable[[], float] = clock

    async def iniciar_async(
        self, uid: str, tipo_transaccion: str, payload: dict[str, object]
    ) -> ResultadoIniciarOobDTO:
        tipo: TipoTransaccionCritica | None = self._clasificador.tipo_desde(tipo_transaccion)
        if tipo is None or not self._clasificador.requiere_oob(tipo):
            return ResultadoIniciarOobDTO(requiere_oob=False)
        try:
            uid_int: int = int(uid)
        except ValueError:
            return ResultadoIniciarOobDTO(
                requiere_oob=True, enviado=False
            )
        usuario: UsuarioEntity | None = await self._usuario_repo.obtener_por_uid_async(uid_int)
        if usuario is None or not usuario.email:
            _logger.warning(
                "OOB sin canal disponible uid=%s tipo=%s",
                uid,
                tipo.value,
                extra=self._campos("fallo", uid, tipo),
            )
            return ResultadoIniciarOobDTO(
                requiere_oob=True, enviado=False
            )
        canal: CanalOob = self._clasificador.canal_para(tipo)
        codigo: str = self._generar_codigo()
        desafio_id: str = secrets.token_urlsafe(18)
        desafio: DesafioOob = DesafioOob(
            desafio_id=desafio_id,
            uid=uid,
            tipo_transaccion=tipo,
            canal=canal,
            payload_hash=self._hash_payload(payload),
            codigo_hash=self._hash(codigo),
            intentos_restantes=self._max_intentos,
            creado_en_monotonic=self._clock(),
            estado=EstadoDesafioOob.PENDIENTE,
        )
        await self._desafio_store.guardar(desafio_id, desafio)
        texto: str
        html: str
        texto, html = self._construir_mensaje(codigo, tipo, usuario.nombre)
        await self._notificador.enviar_async(
            destinatario=usuario.email,
            asunto=OOB_ASUNTO,
            cuerpo_texto=texto,
            cuerpo_html=html,
        )
        _logger.info(
            "OOB desafio emitido uid=%s tipo=%s",
            uid,
            tipo.value,
            extra=self._campos("exito", uid, tipo),
        )
        return ResultadoIniciarOobDTO(
            requiere_oob=True,
            enviado=True,
            desafio_id=desafio_id,
            estado=EstadoDesafioOob.PENDIENTE.value,
            canal=canal.value,
            email_enmascarado=self._enmascarar(usuario.email),
            expira_en_segundos=self._ttl_segundos,
        )

    async def resolver_async(
        self, desafio_id: str, uid: str, aprobar: bool, codigo: str | None
    ) -> ResultadoResolverOobDTO:
        desafio: DesafioOob | None = await self._desafio_store.obtener(desafio_id)
        if desafio is None or desafio.uid != uid:
            raise DesafioOobInvalido(
                "El desafio expiro o no existe. Inicia la operacion de nuevo."
            )
        if not desafio.es_resoluble:
            raise DesafioOobInvalido("El desafio ya fue resuelto.")
        if not aprobar:
            await self._desafio_store.guardar(desafio_id, desafio.rechazado())
            _logger.warning(
                "OOB desafio rechazado por el usuario uid=%s tipo=%s",
                uid,
                desafio.tipo_transaccion.value,
                extra=self._campos("fallo", uid, desafio.tipo_transaccion),
            )
            return ResultadoResolverOobDTO(
                estado=EstadoDesafioOob.RECHAZADA.value, aprobado=False
            )
        if not codigo or not hmac.compare_digest(desafio.codigo_hash, self._hash(codigo)):
            restantes: int = desafio.intentos_restantes - 1
            if restantes <= 0:
                await self._desafio_store.guardar(desafio_id, desafio.bloqueado())
                _logger.warning(
                    "OOB desafio bloqueado por intentos uid=%s",
                    uid,
                    extra=self._campos("fallo", uid, desafio.tipo_transaccion),
                )
                raise DesafioOobInvalido(
                    "Codigo incorrecto. Se agotaron los intentos; inicia la operacion de nuevo.",
                    intentos_restantes=0,
                )
            await self._desafio_store.guardar(desafio_id, desafio.con_intento_consumido())
            raise DesafioOobInvalido("Codigo incorrecto.", intentos_restantes=restantes)
        await self._desafio_store.guardar(desafio_id, desafio.aprobado())
        _logger.info(
            "OOB desafio aprobado uid=%s tipo=%s",
            uid,
            desafio.tipo_transaccion.value,
            extra=self._campos("exito", uid, desafio.tipo_transaccion),
        )
        return ResultadoResolverOobDTO(
            estado=EstadoDesafioOob.APROBADA.value,
            aprobado=True,
            tipo_transaccion=desafio.tipo_transaccion.value,
            payload_hash=desafio.payload_hash,
        )

    # -- Helpers --
    @staticmethod
    def _campos(
        resultado: str, uid: str, tipo: TipoTransaccionCritica
    ) -> dict[str, object]:
        return {
            "evento_seguridad": EVENTO_OOB,
            "resultado": resultado,
            "actor": uid,
            "detalle": tipo.value,
        }

    @staticmethod
    def _generar_codigo() -> str:
        maximo: int = 10**OOB_CODIGO_LONGITUD
        return str(secrets.randbelow(maximo)).zfill(OOB_CODIGO_LONGITUD)

    @staticmethod
    def _hash(codigo: str) -> str:
        return hashlib.sha256(codigo.encode("utf-8")).hexdigest()

    @staticmethod
    def _hash_payload(payload: dict[str, object]) -> str:
        canonico: str = json.dumps(
            payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        )
        return hashlib.sha256(canonico.encode("utf-8")).hexdigest()

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
    def _construir_mensaje(
        codigo: str, tipo: TipoTransaccionCritica, nombre: str
    ) -> tuple[str, str]:
        descripcion: str = DESCRIPCION_TRANSACCION.get(tipo.value, "una operacion sensible")
        saludo: str = ("Hola, " + nombre + ":") if nombre else "Hola:"
        lineas: list[str] = [
            saludo,
            "",
            "Estas confirmando " + descripcion + ". Tu codigo de confirmacion es:",
            "",
            codigo,
            "",
            "Ingresa este codigo para autorizar la operacion. Si no la solicitaste, "
            "RECHAZALA e informa a soporte de inmediato.",
            "",
            "El codigo vence en pocos minutos.",
            "",
            "SUFI",
            "Siempre a tu lado.",
        ]
        texto: str = _NL.join(lineas)
        html: str = (
            "<p>" + saludo + "</p>"
            "<p>Estas confirmando <b>" + descripcion + "</b>. Tu codigo de confirmacion es:</p>"
            '<p style="font-size:24px;font-weight:bold;letter-spacing:3px">' + codigo + "</p>"
            "<p>Ingresa este codigo para autorizar la operacion. Si no la solicitaste, "
            "rechazala e informa a soporte de inmediato.</p>"
            "<p>SUFI<br>Siempre a tu lado.</p>"
        )
        return texto, html
