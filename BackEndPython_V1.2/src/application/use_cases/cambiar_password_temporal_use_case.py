from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from src.application.services.auth_service import AuthService
from src.application.services.login_throttle_service import LoginThrottleService
from src.application.services.servicio_bloqueo_cuenta import ServicioBloqueoCuenta
from src.application.services.servicio_expiracion_password import ServicioExpiracionPassword
from src.application.services.servicio_password_temporal import ServicioPasswordTemporal
from src.application.services.servicio_sesiones import ServicioSesiones
from src.application.use_cases.login_result import LoginResult
from src.domain.entities.modulo_permiso_entity import ModuloPermisoEntity
from src.domain.entities.password_temporal_entity import PasswordTemporalEntity
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.credenciales_invalidas import CredencialesInvalidas
from src.domain.exceptions.password_insegura import PasswordInsegura
from src.domain.ports.outbound.estado_credencial_repository import EstadoCredencialRepository
from src.domain.ports.outbound.frontend_modules_repository import FrontendModulesRepository
from src.domain.ports.outbound.password_history_repository import (
    PasswordHistoryRepository,
)
from src.domain.ports.outbound.usuario_repository import UsuarioRepository
from src.domain.services.validador_password import ValidadorPassword
from src.domain.value_objects.motivo_cierre_sesion import MotivoCierreSesion


class CambiarPasswordTemporalUseCase:
    """AP-0046: cambio obligatorio de la contrasena temporal, SIN sesion previa.

    Espejo del cambio autonomo por vencimiento (AP-0038): autentica con la
    temporal vigente, valida la nueva contrasena con todas las politicas (AP-0044,
    AP-0051, AP-0159, AP-0041) y rechaza que sea igual a la temporal. En exito
    consume la temporal (un solo uso definitivo), reinicia el reloj de vigencia
    (AP-0037 y AP-0042), invalida las sesiones previas (AP-0021, token_version) y
    emite una sesion plena nueva.

    Este flujo OMITE deliberadamente la regla de un cambio por dia (AP-0043): es
    el caso de restablecimiento administrativo documentado como excepcion.
    Reutiliza el retraso incremental (AP-0007) y el bloqueo de cuenta (AP-0009).
    """

    def __init__(
        self,
        auth_service: AuthService,
        usuario_repo: UsuarioRepository,
        modulos_repo: FrontendModulesRepository,
        servicio_temporal: ServicioPasswordTemporal,
        expiracion: ServicioExpiracionPassword,
        throttle: LoginThrottleService,
        validador: ValidadorPassword | None = None,
        sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
        bloqueo: ServicioBloqueoCuenta | None = None,
        estado_credencial: EstadoCredencialRepository | None = None,
        sesiones: ServicioSesiones | None = None,
        historial: PasswordHistoryRepository | None = None,
        historial_tamano: int = 24,
        historial_habilitado: bool = True,
    ) -> None:
        self._auth: AuthService = auth_service
        self._usuario_repo: UsuarioRepository = usuario_repo
        self._modulos_repo: FrontendModulesRepository = modulos_repo
        self._servicio_temporal: ServicioPasswordTemporal = servicio_temporal
        self._expiracion: ServicioExpiracionPassword = expiracion
        self._throttle: LoginThrottleService = throttle
        self._validador: ValidadorPassword | None = validador
        self._sleeper: Callable[[float], Awaitable[None]] = sleeper
        self._bloqueo: ServicioBloqueoCuenta | None = bloqueo
        self._estado_credencial: EstadoCredencialRepository | None = estado_credencial
        self._sesiones: ServicioSesiones | None = sesiones
        self._historial: PasswordHistoryRepository | None = historial
        self._historial_tamano: int = historial_tamano
        self._historial_habilitado: bool = historial_habilitado

    async def ejecutar_async(
        self,
        username: str,
        password_temporal: str,
        nueva_password: str,
        clave_throttle: str,
    ) -> LoginResult:
        clave_cuenta: str = username.strip().lower()
        if self._bloqueo is not None:
            await self._bloqueo.verificar_no_bloqueada(clave_cuenta)

        usuario: UsuarioEntity | None = await self._usuario_repo.obtener_por_nombre_async(
            username
        )
        entidad: PasswordTemporalEntity | None = None
        if usuario is not None:
            # Vencida con match lanza PasswordTemporalVencida (no cuenta como fallo:
            # quien la presenta la conoce). Sin match devuelve None y sigue el
            # tratamiento generico de credenciales invalidas.
            entidad = await self._servicio_temporal.validar_para_cambio(
                usuario.uid or 0, password_temporal
            )
        if usuario is None or entidad is None:
            await self._registrar_fallo(clave_cuenta, username, clave_throttle)
            raise CredencialesInvalidas()

        await self._throttle.reiniciar_async(clave_throttle)
        if self._bloqueo is not None:
            await self._bloqueo.registrar_exito(clave_cuenta)

        uid: int = usuario.uid or 0
        if self._servicio_temporal.coincide(entidad, nueva_password):
            raise PasswordInsegura(
                "La nueva contrasena no puede ser igual a la contrasena temporal."
            )
        await self._auth.establecer_password_async(
            uid,
            nueva_password,
            self._usuario_repo,
            validador=self._validador,
            valores_contextuales=[username],
            hash_actual=usuario.new_pass_hash,
            historial=self._historial if self._historial_habilitado else None,
            historial_tamano=self._historial_tamano,
        )
        await self._servicio_temporal.consumir(entidad)
        await self._expiracion.registrar_cambio(uid)

        token_version: int = 1
        if self._estado_credencial is not None:
            token_version = await self._estado_credencial.incrementar_version(uid)
        # AP-0208: cierra tambien las sesiones en el registro (evidencia por sesion).
        if self._sesiones is not None:
            await self._sesiones.cerrar_todas(uid, MotivoCierreSesion.CAMBIO_CREDENCIAL)
        token: str = self._auth.generar_token(usuario, token_version)
        modulos: list[ModuloPermisoEntity] = (
            await self._modulos_repo.obtener_modulos_por_uid_async(uid)
        )
        return LoginResult(token=token, usuario=usuario, modulos=modulos)

    async def _registrar_fallo(
        self, clave_cuenta: str, username: str, clave_throttle: str
    ) -> None:
        if self._bloqueo is not None:
            existe: bool = (
                await self._usuario_repo.obtener_por_nombre_async(username)
            ) is not None
            await self._bloqueo.registrar_fallo(clave_cuenta, existe)
        espera_segundos: int = await self._throttle.registrar_fallo_async(clave_throttle)
        if espera_segundos > 0:
            await self._sleeper(espera_segundos)
