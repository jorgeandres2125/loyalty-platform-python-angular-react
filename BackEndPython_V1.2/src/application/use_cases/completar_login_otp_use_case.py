from __future__ import annotations

from src.application.services.auth_service import AuthService
from src.application.services.servicio_otp_login import ServicioOtpLogin
from src.application.use_cases.login_result import LoginResult
from src.domain.entities.modulo_permiso_entity import ModuloPermisoEntity
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.otp_invalido import OtpInvalido
from src.domain.ports.outbound.estado_credencial_repository import EstadoCredencialRepository
from src.domain.ports.outbound.frontend_modules_repository import FrontendModulesRepository
from src.domain.ports.outbound.usuario_repository import UsuarioRepository
from src.shared.constants.otp_login import AMR_OTP, AMR_PASSWORD


class CompletarLoginOtpUseCase:
    """AP-0012: completa el login tras verificar el segundo factor OTP.

    Verifica el codigo OTP (un solo uso) y, si es correcto, emite el token con
    amr=[pwd, otp] reflejando que la autenticacion uso dos factores. Reutiliza la version
    de credencial (AP-0021) para el claim tv.
    """

    def __init__(
        self,
        otp: ServicioOtpLogin,
        auth_service: AuthService,
        usuario_repo: UsuarioRepository,
        modulos_repo: FrontendModulesRepository,
        estado_credencial: EstadoCredencialRepository | None = None,
    ) -> None:
        self._otp: ServicioOtpLogin = otp
        self._auth: AuthService = auth_service
        self._usuario_repo: UsuarioRepository = usuario_repo
        self._modulos_repo: FrontendModulesRepository = modulos_repo
        self._estado_credencial: EstadoCredencialRepository | None = estado_credencial

    async def completar_async(self, desafio_id: str, codigo: str) -> LoginResult:
        uid: int = await self._otp.verificar_async(desafio_id, codigo)
        usuario: UsuarioEntity | None = await self._usuario_repo.obtener_por_uid_async(uid)
        if usuario is None:
            raise OtpInvalido("La cuenta no esta disponible. Inicia sesion de nuevo.")
        token_version: int = 1
        if self._estado_credencial is not None:
            token_version = await self._estado_credencial.obtener_version(uid)
        token: str = self._auth.generar_token(
            usuario, token_version, amr=[AMR_PASSWORD, AMR_OTP]
        )
        modulos: list[ModuloPermisoEntity] = (
            await self._modulos_repo.obtener_modulos_por_uid_async(uid)
        )
        return LoginResult(token=token, usuario=usuario, modulos=modulos)
