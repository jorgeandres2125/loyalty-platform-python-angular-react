from __future__ import annotations

import logging

from src.application.services.servicio_bloqueo_cuenta import ServicioBloqueoCuenta
from src.application.services.servicio_sesiones import ServicioSesiones
from src.domain.exceptions.cuenta_bloqueada import CuentaBloqueada
from src.domain.exceptions.sesion_invalida import SesionInvalida
from src.domain.ports.outbound.estado_credencial_repository import EstadoCredencialRepository
from src.domain.ports.outbound.revocacion_token_store import RevocacionTokenStore
from src.domain.ports.outbound.usuario_repository import UsuarioRepository
from src.domain.value_objects.estado_usuario import EstadoUsuario
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD
from src.shared.constants.sesion import (
    CLAIM_JTI,
    CLAIM_SID,
    CLAIM_TOKEN_VERSION,
    EVENTO_SESION,
    TOKEN_VERSION_INICIAL,
)

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)


class ValidadorSesion:
    """AP-0021: revalida en cada peticion que la credencial siga siendo valida.

    Mas alla de firma y exp del JWT, verifica: (1) la cuenta no esta bloqueada (AP-0009,
    por el nombre de usuario del token); (2) el token_version del token coincide con la
    version actual del usuario (revocacion masiva: cambio de contrasena, cierre de sesion
    global, deshabilitacion); (3) el jti no esta revocado (cierre de sesion puntual);
    (4) AP-0049: el usuario sigue existiendo y activo (cubre la eliminacion y la
    deshabilitacion hecha fuera de los flujos de la aplicacion).
    Fail-closed: cualquier discrepancia lanza SesionInvalida (401) o propaga
    CuentaBloqueada (403). Un token sin tv se trata como version inicial (migracion).
    """

    def __init__(
        self,
        estado_repo: EstadoCredencialRepository,
        denylist: RevocacionTokenStore,
        bloqueo: ServicioBloqueoCuenta,
        usuario_repo: UsuarioRepository | None = None,
        sesiones: ServicioSesiones | None = None,
    ) -> None:
        self._estado_repo: EstadoCredencialRepository = estado_repo
        self._denylist: RevocacionTokenStore = denylist
        self._bloqueo: ServicioBloqueoCuenta = bloqueo
        self._usuario_repo: UsuarioRepository | None = usuario_repo
        self._sesiones: ServicioSesiones | None = sesiones

    async def validar(self, claims: dict[str, object]) -> None:
        nombre: str = str(claims.get("nombre", "")).strip().lower()
        if nombre:
            try:
                await self._bloqueo.verificar_no_bloqueada(nombre)
            except CuentaBloqueada:
                # AP-0133: usuario bloqueado (AP-0009) pierde el acceso de inmediato.
                _logger.warning(
                    "AP-0133 cuenta bloqueada usuario=%s estado=%s",
                    nombre,
                    EstadoUsuario.BLOQUEADO.value,
                    extra=self._campos("cuenta_bloqueada", nombre),
                )
                raise

        uid: int = self._uid(claims)
        if self._usuario_repo is not None:
            # AP-0133 y AP-0049: verificacion viva del estado por peticion. Un usuario
            # inhabilitado o eliminado pierde el acceso de inmediato, aunque su JWT siga
            # vigente. Se audita el estado concreto que denego (AP-0022).
            estado: EstadoUsuario = await self._usuario_repo.resolver_estado(uid)
            if estado is not EstadoUsuario.ACTIVO:
                _logger.warning(
                    "AP-0133 cuenta no activa uid=%s estado=%s",
                    uid,
                    estado.value,
                    extra=self._campos(f"cuenta_{estado.value}", str(uid)),
                )
                raise SesionInvalida("credencial revocada o expirada")
        tv_token: int = self._version_token(claims)
        tv_actual: int = await self._estado_repo.obtener_version(uid)
        if tv_token != tv_actual:
            _logger.warning(
                "AP-0021 token_version obsoleta uid=%s",
                uid,
                extra=self._campos("revocado_version", str(uid)),
            )
            raise SesionInvalida("credencial revocada o expirada")

        jti: object = claims.get(CLAIM_JTI)
        if isinstance(jti, str) and jti and await self._denylist.esta_revocado(jti):
            _logger.warning(
                "AP-0021 jti revocado uid=%s",
                uid,
                extra=self._campos("revocado_jti", str(uid)),
            )
            raise SesionInvalida("sesion cerrada")

        if self._sesiones is not None:
            # AP-0130: la sesion (sid) pudo cerrarse desde otro dispositivo (cierre
            # remoto) o por expulsion de concurrencia, aunque el jti actual siga vivo.
            sid: object = claims.get(CLAIM_SID)
            if isinstance(sid, str) and sid and await self._sesiones.esta_revocada(sid):
                _logger.warning(
                    "AP-0130 sesion revocada uid=%s",
                    uid,
                    extra=self._campos("revocado_sesion", str(uid)),
                )
                raise SesionInvalida("sesion cerrada remotamente")

    @staticmethod
    def _uid(claims: dict[str, object]) -> int:
        try:
            return int(str(claims.get("sub", "0")))
        except ValueError as exc:
            raise SesionInvalida("sujeto invalido") from exc

    @staticmethod
    def _version_token(claims: dict[str, object]) -> int:
        valor: object = claims.get(CLAIM_TOKEN_VERSION, TOKEN_VERSION_INICIAL)
        if isinstance(valor, bool):
            return TOKEN_VERSION_INICIAL
        if isinstance(valor, int):
            return valor
        if isinstance(valor, str) and valor.isdigit():
            return int(valor)
        return TOKEN_VERSION_INICIAL

    @staticmethod
    def _campos(motivo: str, actor: str) -> dict[str, object]:
        return {
            "evento_seguridad": EVENTO_SESION,
            "resultado": "fallo",
            "actor": actor,
            "detalle": motivo,
        }
