from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from collections.abc import Callable
from datetime import UTC, datetime
from urllib.parse import urlencode

from src.application.dto.resultado_solicitud_codigo_dto import ResultadoSolicitudCodigoDTO
from src.application.dto.resultado_verificacion_dto import ResultadoVerificacionDTO
from src.domain.entities.historico_correo_entity import HistoricoCorreoEntity
from src.domain.entities.perfil_contacto_entity import PerfilContactoEntity
from src.domain.exceptions.codigo_invalido import CodigoInvalido
from src.domain.ports.outbound.codigo_verificacion_store import CodigoVerificacionStore
from src.domain.ports.outbound.historico_correo_repository import HistoricoCorreoRepository
from src.domain.ports.outbound.notificador_correo import NotificadorCorreo
from src.domain.ports.outbound.perfil_repository import PerfilRepository
from src.domain.value_objects.codigo_verificacion import CodigoVerificacion
from src.shared.constants.verificacion_email import (
    ASUNTO_VERIFICACION,
    CODIGO_LONGITUD,
    REMITENTE_SISTEMA,
    TIPO_CORREO_VERIFICACION,
)


class VerificarEmailUseCase:
    """AP-0004 — Verificación de propiedad del correo por doble opt-in.

    `solicitar_codigo_async` genera un OTP de N dígitos, lo envía al correo ya
    declarado en el perfil (descifrado de users_perfil_contacto.email_enc) y guarda
    solo su hash en un almacén con TTL de 24h. `confirmar_codigo_async` compara el
    código y, si coincide, marca email_verificado = 1.

    Reglas de seguridad centralizadas (testeables sin HTTP):
    * Anti-enumeración: ante documento inexistente / sin correo se devuelve
      `enviado=False` sin distinguir el caso.
    * Cooldown de reenvío: no se regenera un código si el anterior es más reciente
      que `cooldown_segundos`.
    * Intentos limitados: cada confirmación fallida consume un intento; agotados,
      el código se invalida y hay que solicitar uno nuevo.
    * Un solo uso: al confirmar con éxito el código se elimina del almacén.
    """

    def __init__(
        self,
        perfil_repo: PerfilRepository,
        codigo_store: CodigoVerificacionStore,
        notificador: NotificadorCorreo,
        historico_repo: HistoricoCorreoRepository,
        ttl_horas: int,
        max_intentos: int,
        cooldown_segundos: int,
        frontend_base_url: str = "",
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._perfil_repo: PerfilRepository = perfil_repo
        self._codigo_store: CodigoVerificacionStore = codigo_store
        self._notificador: NotificadorCorreo = notificador
        self._historico_repo: HistoricoCorreoRepository = historico_repo
        self._ttl_horas: int = ttl_horas
        self._max_intentos: int = max_intentos
        self._cooldown_segundos: int = cooldown_segundos
        self._frontend_base_url: str = frontend_base_url
        self._clock: Callable[[], float] = clock

    # ── Operaciones ──────────────────────────────────────────────────────────

    async def solicitar_codigo_async(
        self,
        tipo_documento: str,
        numero_documento: str,
    ) -> ResultadoSolicitudCodigoDTO:
        perfil: PerfilContactoEntity | None = await self._perfil_repo.obtener_contacto_async(
            numero_documento
        )
        # Anti-enumeración: no revelar si el documento existe, si tiene correo, ni si
        # el tipo de documento coincide. Cualquiera de esos casos → respuesta neutra.
        if (
            perfil is None
            or not perfil.email
            or not self._tipos_coinciden(perfil.tipo_documento, tipo_documento)
        ):
            return ResultadoSolicitudCodigoDTO(enviado=False)

        clave: str = self._clave(tipo_documento, numero_documento)
        ahora: float = self._clock()
        existente: CodigoVerificacion | None = await self._codigo_store.obtener(clave)
        en_cooldown: bool = (
            existente is not None
            and (ahora - existente.creado_en_monotonic) < self._cooldown_segundos
        )
        if en_cooldown:
            return ResultadoSolicitudCodigoDTO(
                enviado=False,
                email_enmascarado=self._enmascarar(perfil.email),
                expira_en_horas=self._ttl_horas,
                en_cooldown=True,
            )

        codigo: str = self._generar_codigo()
        registro: CodigoVerificacion = CodigoVerificacion(
            codigo_hash=self._hash(codigo),
            intentos_restantes=self._max_intentos,
            creado_en_monotonic=ahora,
        )
        await self._codigo_store.guardar(clave, registro)

        cuerpo_texto: str
        cuerpo_html: str
        cuerpo_texto, cuerpo_html = self._construir_mensaje(
            codigo,
            perfil.nombre_completo,
            self._frontend_base_url,
            tipo_documento,
            numero_documento,
        )
        await self._notificador.enviar_async(
            destinatario=perfil.email,
            asunto=ASUNTO_VERIFICACION,
            cuerpo_texto=cuerpo_texto,
            cuerpo_html=cuerpo_html,
        )
        await self._historico_repo.registrar_async(
            HistoricoCorreoEntity(
                tipo_correo=TIPO_CORREO_VERIFICACION,
                usuario_envio=REMITENTE_SISTEMA,
                usuario_destino=perfil.email,
                fecha=self._ahora_utc(),
                enviado=True,
            )
        )
        return ResultadoSolicitudCodigoDTO(
            enviado=True,
            email_enmascarado=self._enmascarar(perfil.email),
            expira_en_horas=self._ttl_horas,
        )

    async def confirmar_codigo_async(
        self,
        tipo_documento: str,
        numero_documento: str,
        codigo: str,
    ) -> ResultadoVerificacionDTO:
        clave: str = self._clave(tipo_documento, numero_documento)
        registro: CodigoVerificacion | None = await self._codigo_store.obtener(clave)
        if registro is None:
            raise CodigoInvalido("El código expiró o no existe. Solicita uno nuevo.")

        if hmac.compare_digest(registro.codigo_hash, self._hash(codigo)):
            await self._codigo_store.eliminar(clave)
            await self._perfil_repo.marcar_email_verificado_async(
                numero_documento, self._ahora_utc()
            )
            return ResultadoVerificacionDTO(verificado=True, numero_documento=numero_documento)

        restantes: int = registro.intentos_restantes - 1
        if restantes <= 0:
            await self._codigo_store.eliminar(clave)
            raise CodigoInvalido(
                "Código incorrecto. Se agotaron los intentos; solicita uno nuevo.",
                intentos_restantes=0,
            )
        await self._codigo_store.guardar(clave, registro.con_intento_consumido())
        raise CodigoInvalido("Código incorrecto.", intentos_restantes=restantes)

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _clave(tipo_documento: str, numero_documento: str) -> str:
        return f"{tipo_documento}:{numero_documento}"

    @staticmethod
    def _tipos_coinciden(almacenado: str, recibido: str) -> bool:
        # Formatos equivalentes del tipo de documento ("C.C." == "CC"): el dato
        # legado es inconsistente, así que se ignoran mayúsculas y no-alfanuméricos.
        norm_alm: str = "".join(ch for ch in almacenado.upper() if ch.isalnum())
        norm_rec: str = "".join(ch for ch in recibido.upper() if ch.isalnum())
        return norm_alm == norm_rec

    @staticmethod
    def _hash(codigo: str) -> str:
        return hashlib.sha256(codigo.encode("utf-8")).hexdigest()

    @staticmethod
    def _ahora_utc() -> datetime:
        # naive UTC para encajar en DATETIME2 (SQL Server no almacena tzinfo).
        return datetime.now(UTC).replace(tzinfo=None)

    @staticmethod
    def _enmascarar(email: str) -> str:
        local: str
        dominio: str
        try:
            local, dominio = email.split("@", 1)
        except ValueError:
            return "***"
        visible: str = local[0] if local else "*"
        return f"{visible}***@{dominio}"

    @staticmethod
    def _generar_codigo() -> str:
        maximo: int = 10**CODIGO_LONGITUD
        return str(secrets.randbelow(maximo)).zfill(CODIGO_LONGITUD)

    @staticmethod
    def _construir_mensaje(
        codigo: str,
        nombre: str,
        frontend_base_url: str,
        tipo_documento: str,
        numero_documento: str,
    ) -> tuple[str, str]:
        saludo: str = f"Hola, {nombre}:" if nombre else "Hola:"
        # El enlace lleva el documento (no el código) para que el formulario aterrice
        # directo en el paso de ingresar el código. El código sigue siendo el secreto.
        query: str = urlencode({"doc": numero_documento, "tipo": tipo_documento})
        enlace: str = (
            f"{frontend_base_url.rstrip('/')}/verificar-correo?{query}"
            if frontend_base_url
            else ""
        )
        instruccion: str = (
            "Para confirmar que este correo te pertenece, ingresa este código en el "
            "formulario de verificación."
        )
        texto_enlace: str = f"\n\nAbre el formulario aquí: {enlace}" if enlace else ""
        texto: str = (
            f"{saludo}\n\n"
            "Tu código de verificación de correo es:\n\n"
            f"{codigo}\n\n"
            f"{instruccion}{texto_enlace}\n\n"
            "El código vence en 24 horas. Si no solicitaste esta verificación, puedes "
            "ignorar este mensaje.\n\n"
            "SUFI\n"
            "Siempre a tu lado."
        )
        # En HTML el '&' del query debe ir escapado; el cliente lo restaura al navegar.
        enlace_html: str = enlace.replace("&", "&amp;")
        boton_html: str = (
            f'<p style="margin:24px 0"><a href="{enlace_html}" '
            'style="background:#100941;color:#ffffff;text-decoration:none;padding:12px 24px;'
            'border-radius:8px;display:inline-block;font-weight:bold">Verificar mi correo</a></p>'
            if enlace
            else ""
        )
        html: str = (
            f"<p>{saludo}</p>"
            "<p>Tu código de verificación de correo es:</p>"
            f'<p style="font-size:24px;font-weight:bold;letter-spacing:3px">{codigo}</p>'
            f"<p>{instruccion}</p>"
            f"{boton_html}"
            "<p>El código vence en 24 horas. Si no solicitaste esta verificación, puedes "
            "ignorar este mensaje.</p>"
            "<p>SUFI<br>Siempre a tu lado.</p>"
        )
        return texto, html
