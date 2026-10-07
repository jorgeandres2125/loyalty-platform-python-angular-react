from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from src.application.services.auth_service import AuthService
from src.application.services.login_throttle_service import LoginThrottleService
from src.application.services.servicio_bloqueo_cuenta import ServicioBloqueoCuenta
from src.application.services.servicio_expiracion_password import ServicioExpiracionPassword
from src.application.services.servicio_sesiones import ServicioSesiones
from src.application.use_cases.login_result import LoginResult
from src.domain.entities.modulo_permiso_entity import ModuloPermisoEntity
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.credencial_vencida_fuera_de_gracia import (
    CredencialVencidaFueraDeGracia,
)
from src.domain.exceptions.credencial_vigente import CredencialVigente
from src.domain.exceptions.credenciales_invalidas import CredencialesInvalidas
from src.domain.ports.outbound.estado_credencial_repository import EstadoCredencialRepository
from src.domain.ports.outbound.frontend_modules_repository import FrontendModulesRepository
from src.domain.ports.outbound.password_history_repository import (
    PasswordHistoryRepository,
)
from src.domain.ports.outbound.usuario_repository import UsuarioRepository
from src.domain.services.validador_password import ValidadorPassword
from src.domain.value_objects.estado_credencial import EstadoCredencial
from src.domain.value_objects.estado_credencial_info import EstadoCredencialInfo
from src.domain.value_objects.motivo_cierre_sesion import MotivoCierreSesion


class CambiarPasswordExpiradaUseCase:
    """AP-0038: cambio autonomo de contrasena dentro de la ventana de gracia posterior
    al vencimiento, SIN sesion previa.

    Autentica con la contrasena vencida (que el usuario aun conoce), clasifica el estado
    y solo permite el cambio si esta EN_GRACIA. Fuera de gracia (o vigente) lo rechaza.
    Reutiliza el retraso incremental (AP-0007) y el bloqueo de cuenta (AP-0009) para
    resistir fuerza bruta. En exito reinicia el reloj de vencimiento, invalida las
    sesiones previas (token_version, AP-0021) y emite una sesion plena nueva.

    El orden es deliberado: se autentica ANTES de clasificar para no revelar el estado
    de vencimiento a quien no posee la contrasena valida.
    """

    def __init__(
        self,
        auth_service: AuthService,
        usuario_repo: UsuarioRepository,
        modulos_repo: FrontendModulesRepository,
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
        password_actual: str,
        nueva_password: str,
        clave_throttle: str,
    ) -> LoginResult:
        clave_cuenta: str = username.strip().lower()
        if self._bloqueo is not None:
            await self._bloqueo.verificar_no_bloqueada(clave_cuenta)

        usuario: UsuarioEntity | None = await self._auth.autenticar_async(
            username, password_actual, self._usuario_repo
        )
        if usuario is None:
            await self._registrar_fallo(clave_cuenta, username, clave_throttle)
            raise CredencialesInvalidas()

        await self._throttle.reiniciar_async(clave_throttle)
        if self._bloqueo is not None:
            await self._bloqueo.registrar_exito(clave_cuenta)

        uid: int = usuario.uid or 0
        info: EstadoCredencialInfo = await self._expiracion.evaluar_estado(uid)
        if info.estado == EstadoCredencial.VIGENTE:
            raise CredencialVigente()
        if info.estado == EstadoCredencial.FUERA_GRACIA:
            raise CredencialVencidaFueraDeGracia(info.dias_desde_vencimiento)

        # EN_GRACIA: aplica la nueva contrasena (valida y rechaza que sea igual a la actual).
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
        await self._expiracion.registrar_cambio(uid)

        token_version: int = 1
        if self._estado_credencial is not None:
            token_version = await self._estado_credencial.incrementar_version(uid)
        # AP-0208: ademas de invalidar los JWT (token_version), cierra las sesiones en
        # el Session Registry para que la lista de AP-0207 no muestre sesiones muertas
        # y quede evidencia por sesion del motivo del cierre.
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
