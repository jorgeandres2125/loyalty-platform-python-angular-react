from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from src.application.services.auth_service import AuthService
from src.application.services.login_throttle_service import LoginThrottleService
from src.application.services.servicio_bloqueo_cuenta import ServicioBloqueoCuenta
from src.application.services.servicio_bloqueo_duro import ServicioBloqueoDuro
from src.application.services.servicio_expiracion_password import ServicioExpiracionPassword
from src.application.services.servicio_otp_login import ServicioOtpLogin
from src.application.services.servicio_password_temporal import ServicioPasswordTemporal
from src.application.use_cases.login_result import LoginResult
from src.domain.entities.modulo_permiso_entity import ModuloPermisoEntity
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.credencial_en_gracia import CredencialEnGracia
from src.domain.exceptions.credencial_vencida_fuera_de_gracia import (
    CredencialVencidaFueraDeGracia,
)
from src.domain.exceptions.credenciales_invalidas import CredencialesInvalidas
from src.domain.exceptions.otp_requerido import OtpRequerido
from src.domain.ports.outbound.estado_credencial_repository import EstadoCredencialRepository
from src.domain.ports.outbound.frontend_modules_repository import FrontendModulesRepository
from src.domain.ports.outbound.usuario_repository import UsuarioRepository
from src.domain.value_objects.estado_credencial import EstadoCredencial
from src.domain.value_objects.estado_credencial_info import EstadoCredencialInfo


class LoginUseCase:
    """Caso de uso de inicio de sesion â€” orquesta autenticacion, retraso incremental
    (AP-0007) y bloqueo de cuenta por intentos fallidos (AP-0009).

    Flujo: si la cuenta esta bloqueada (AP-0009) se rechaza antes de verificar la
    contrasena. Se autentica por nombre de usuario; ante fallo suma un intento a la
    cuenta (AP-0009) y a la clave IP|usuario (AP-0007), aplica el retraso incremental
    (5 s -> max 30 s) y lanza CredencialesInvalidas; ante exito reinicia ambos
    contadores, firma el JWT y resuelve los modulos del usuario.

    El bloqueo se inyecta opcionalmente: si es None, el login se comporta como antes de
    AP-0009 (sin bloqueo de cuenta). `sleeper` se inyecta para que los tests no esperen.
    """

    def __init__(
        self,
        auth_service: AuthService,
        throttle: LoginThrottleService,
        usuario_repo: UsuarioRepository,
        modulos_repo: FrontendModulesRepository,
        sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
        bloqueo: ServicioBloqueoCuenta | None = None,
        estado_credencial: EstadoCredencialRepository | None = None,
        otp: ServicioOtpLogin | None = None,
        expiracion: ServicioExpiracionPassword | None = None,
        enforcement_enabled: bool = False,
        password_temporal: ServicioPasswordTemporal | None = None,
        bloqueo_duro: ServicioBloqueoDuro | None = None,
    ) -> None:
        self._auth: AuthService = auth_service
        self._throttle: LoginThrottleService = throttle
        self._usuario_repo: UsuarioRepository = usuario_repo
        self._modulos_repo: FrontendModulesRepository = modulos_repo
        self._sleeper: Callable[[float], Awaitable[None]] = sleeper
        self._bloqueo: ServicioBloqueoCuenta | None = bloqueo
        self._estado_credencial: EstadoCredencialRepository | None = estado_credencial
        self._otp: ServicioOtpLogin | None = otp
        self._expiracion: ServicioExpiracionPassword | None = expiracion
        self._enforcement_enabled: bool = enforcement_enabled
        self._password_temporal: ServicioPasswordTemporal | None = password_temporal
        self._bloqueo_duro: ServicioBloqueoDuro | None = bloqueo_duro

    async def ejecutar_async(
        self, username: str, password: str, clave_throttle: str
    ) -> LoginResult:
        clave_cuenta: str = username.strip().lower()
        if self._bloqueo_duro is not None:
            # AP-0157: el bloqueo duro tiene precedencia absoluta; se verifica antes que el
            # suave y antes de validar la credencial. Requiere resolver el uid del usuario.
            usuario_hard: UsuarioEntity | None = (
                await self._usuario_repo.obtener_por_nombre_async(username)
            )
            if usuario_hard is not None:
                await self._bloqueo_duro.verificar_no_bloqueada(usuario_hard.uid or 0)
        if self._bloqueo is not None:
            # AP-0009: rechaza antes de verificar la contrasena si la cuenta esta bloqueada.
            await self._bloqueo.verificar_no_bloqueada(clave_cuenta)

        usuario: UsuarioEntity | None = await self._auth.autenticar_async(
            username, password, self._usuario_repo
        )
        if usuario is None:
            if self._password_temporal is not None:
                # AP-0046: puede tratarse de una contrasena temporal. Con match vigente
                # lanza PasswordTemporalRequiereCambio y con match vencido (AP-0048)
                # PasswordTemporalVencida; ninguno cuenta como fallo AP-0007 ni AP-0009
                # (quien la presenta la conoce). Sin match, sigue el flujo de fallo.
                await self._password_temporal.verificar_login(
                    username, password, self._usuario_repo
                )
            if self._bloqueo is not None:
                # AP-0009: suma el fallo a la cuenta y la bloquea al alcanzar el maximo.
                existe: bool = (
                    await self._usuario_repo.obtener_por_nombre_async(username)
                ) is not None
                await self._bloqueo.registrar_fallo(clave_cuenta, existe)
            espera_segundos: int = await self._throttle.registrar_fallo_async(clave_throttle)
            if espera_segundos > 0:
                await self._sleeper(espera_segundos)
            raise CredencialesInvalidas()

        await self._throttle.reiniciar_async(clave_throttle)
        if self._bloqueo is not None:
            # AP-0009: login exitoso -> reinicia el contador de fallos de la cuenta.
            await self._bloqueo.registrar_exito(clave_cuenta)
        if self._expiracion is not None and self._enforcement_enabled:
            # AP-0038: si la contrasena vencio no se emite sesion plena. En gracia se
            # exige el cambio autonomo; fuera de gracia se bloquea (restablecimiento).
            info: EstadoCredencialInfo = await self._expiracion.evaluar_estado(
                usuario.uid or 0
            )
            if info.estado == EstadoCredencial.FUERA_GRACIA:
                raise CredencialVencidaFueraDeGracia(info.dias_desde_vencimiento)
            if info.estado == EstadoCredencial.EN_GRACIA:
                raise CredencialEnGracia(
                    info.dias_desde_vencimiento, info.dias_restantes_gracia
                )
        if self._otp is not None and self._otp.requiere_otp(usuario):
            # AP-0012: usuario critico -> exige segundo factor OTP; se emite el desafio y
            # el login no entrega token hasta verificarlo (paso 2 del login).
            desafio = await self._otp.emitir_desafio_async(usuario)
            raise OtpRequerido(
                desafio.desafio_id, desafio.email_enmascarado, desafio.expira_en_segundos
            )
        token_version: int = 1
        if self._estado_credencial is not None:
            # AP-0021: embebe la version de credencial actual en el token (claim tv).
            token_version = await self._estado_credencial.obtener_version(usuario.uid or 0)
        token: str = self._auth.generar_token(usuario, token_version)
        modulos: list[ModuloPermisoEntity] = await self._modulos_repo.obtener_modulos_por_uid_async(
            usuario.uid or 0
        )
        return LoginResult(token=token, usuario=usuario, modulos=modulos)
