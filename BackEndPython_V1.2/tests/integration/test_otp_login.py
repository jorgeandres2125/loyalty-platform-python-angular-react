from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.services.auth_service import AuthService
from src.application.services.login_throttle_service import LoginThrottleService
from src.application.services.servicio_otp_login import ServicioOtpLogin
from src.application.use_cases.completar_login_otp_use_case import CompletarLoginOtpUseCase
from src.application.use_cases.login_use_case import LoginUseCase
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.otp_invalido import OtpInvalido
from src.domain.exceptions.otp_requerido import OtpRequerido
from src.domain.value_objects.rol_usuario import RolUsuario
from src.infrastructure.external.in_memory_desafio_otp_store import InMemoryDesafioOtpStore
from src.infrastructure.external.in_memory_intentos_login_store import InMemoryIntentosLoginStore
from src.infrastructure.security.jwt_handler import JWTHandler
from src.infrastructure.security.password_hasher import PasswordHasher

NL = chr(10)
_ROLES_CRIT = frozenset({"administrator", "webmaster", "documentador"})


class FakeNotificador:
    def __init__(self) -> None:
        self.enviados: list[tuple[str, str, str, str]] = []

    async def enviar_async(self, destinatario, asunto, cuerpo_texto, cuerpo_html) -> None:
        self.enviados.append((destinatario, asunto, cuerpo_texto, cuerpo_html))

    async def enviar_masivo_async(self, destinatarios, asunto, cuerpo_texto, cuerpo_html) -> None:
        self.enviados.append((",".join(destinatarios), asunto, cuerpo_texto, cuerpo_html))


def _usuario(uid: int = 1, roles=None, email: str = "admin@sufi.co") -> UsuarioEntity:
    return UsuarioEntity(
        uid=uid,
        nombre=str(uid),
        email=email,
        roles=roles or [RolUsuario.ADMINISTRATOR],
        activo=True,
    )


def _servicio(
    notif=None, enabled: bool = True, max_intentos: int = 3, ttl: int = 300
) -> ServicioOtpLogin:
    return ServicioOtpLogin(
        desafio_store=InMemoryDesafioOtpStore(ttl_segundos=ttl),
        notificador=notif or FakeNotificador(),
        roles_criticos=_ROLES_CRIT,
        max_intentos=max_intentos,
        ttl_segundos=ttl,
        enabled=enabled,
    )


def _codigo_de(notif: FakeNotificador) -> str:
    for linea in notif.enviados[-1][2].split(NL):
        if linea.isdigit() and len(linea) == 6:
            return linea
    raise AssertionError("no se encontro codigo")


class TestRequiereOtp:
    def test_rol_critico_requiere(self) -> None:
        assert _servicio().requiere_otp(_usuario(roles=[RolUsuario.ADMINISTRATOR])) is True

    def test_rol_no_critico_no_requiere(self) -> None:
        assert _servicio().requiere_otp(_usuario(roles=[RolUsuario.COMISIONISTA])) is False

    def test_deshabilitado_no_requiere(self) -> None:
        assert _servicio(enabled=False).requiere_otp(_usuario()) is False

    def test_sin_correo_no_requiere(self) -> None:
        assert _servicio().requiere_otp(_usuario(email="")) is False


class TestDesafioOtp:
    async def test_emitir_y_verificar_un_solo_uso(self) -> None:
        notif = FakeNotificador()
        svc = _servicio(notif)
        res = await svc.emitir_desafio_async(_usuario(uid=9))
        assert res.desafio_id
        assert res.email_enmascarado == "a***@sufi.co"
        assert len(notif.enviados) == 1
        codigo = _codigo_de(notif)
        assert await svc.verificar_async(res.desafio_id, codigo) == 9
        with pytest.raises(OtpInvalido):
            await svc.verificar_async(res.desafio_id, codigo)

    async def test_codigo_incorrecto_consume_intento(self) -> None:
        svc = _servicio(FakeNotificador(), max_intentos=3)
        res = await svc.emitir_desafio_async(_usuario())
        with pytest.raises(OtpInvalido) as exc:
            await svc.verificar_async(res.desafio_id, "000000")
        assert exc.value.intentos_restantes == 2

    async def test_bloqueo_por_intentos(self) -> None:
        svc = _servicio(FakeNotificador(), max_intentos=1)
        res = await svc.emitir_desafio_async(_usuario())
        with pytest.raises(OtpInvalido) as exc:
            await svc.verificar_async(res.desafio_id, "000000")
        assert exc.value.intentos_restantes == 0

    async def test_desafio_inexistente(self) -> None:
        with pytest.raises(OtpInvalido):
            await _servicio().verificar_async("noexiste", "000000")


async def _no_sleep(_s: float) -> None:
    return None


def _login_uc(otp: ServicioOtpLogin, autenticar_return) -> LoginUseCase:
    auth = AsyncMock()
    auth.autenticar_async.return_value = autenticar_return
    auth.generar_token = MagicMock(return_value="tok")
    throttle = LoginThrottleService(
        store=InMemoryIntentosLoginStore(ttl_segundos=900), paso_segundos=5, maximo_segundos=30
    )
    modulos_repo = AsyncMock()
    modulos_repo.obtener_modulos_por_uid_async.return_value = []
    return LoginUseCase(
        auth_service=auth,
        throttle=throttle,
        usuario_repo=AsyncMock(),
        modulos_repo=modulos_repo,
        sleeper=_no_sleep,
        otp=otp,
    )


class TestLoginUseCasePaso1:
    async def test_usuario_critico_exige_otp(self) -> None:
        uc = _login_uc(_servicio(), _usuario(roles=[RolUsuario.ADMINISTRATOR]))
        with pytest.raises(OtpRequerido):
            await uc.ejecutar_async("admin", "pw", "ip|admin")

    async def test_usuario_no_critico_recibe_token(self) -> None:
        uc = _login_uc(_servicio(), _usuario(roles=[RolUsuario.COMISIONISTA]))
        result = await uc.ejecutar_async("com", "pw", "ip|com")
        assert result.token == "tok"


class TestCompletarLoginOtp:
    async def test_completa_y_emite_token_con_amr(self) -> None:
        notif = FakeNotificador()
        svc = _servicio(notif)
        usuario = _usuario(uid=5, roles=[RolUsuario.ADMINISTRATOR])
        res = await svc.emitir_desafio_async(usuario)
        codigo = _codigo_de(notif)
        auth = AsyncMock()
        auth.generar_token = MagicMock(return_value="tok2")
        usuario_repo = AsyncMock()
        usuario_repo.obtener_por_uid_async.return_value = usuario
        modulos_repo = AsyncMock()
        modulos_repo.obtener_modulos_por_uid_async.return_value = []
        uc = CompletarLoginOtpUseCase(
            otp=svc, auth_service=auth, usuario_repo=usuario_repo, modulos_repo=modulos_repo
        )
        result = await uc.completar_async(res.desafio_id, codigo)
        assert result.token == "tok2"
        _, kwargs = auth.generar_token.call_args
        assert kwargs["amr"] == ["pwd", "otp"]

    async def test_codigo_malo_no_emite(self) -> None:
        notif = FakeNotificador()
        svc = _servicio(notif)
        res = await svc.emitir_desafio_async(_usuario())
        auth = AsyncMock()
        auth.generar_token = MagicMock()
        uc = CompletarLoginOtpUseCase(
            otp=svc, auth_service=auth, usuario_repo=AsyncMock(), modulos_repo=AsyncMock()
        )
        with pytest.raises(OtpInvalido):
            await uc.completar_async(res.desafio_id, "000000")
        auth.generar_token.assert_not_called()


def _auth() -> AuthService:
    return AuthService(
        jwt_handler=JWTHandler("test-secret-key-min-32-chars-xxxxx", "HS256"),
        password_hasher=PasswordHasher(),
        jwt_expire_minutes=60,
    )


class TestAmrEnToken:
    def test_token_por_defecto_amr_pwd(self) -> None:
        payload = _auth().verificar_token(_auth().generar_token(_usuario()))
        assert payload["amr"] == ["pwd"]

    def test_token_con_otp_amr_pwd_otp(self) -> None:
        auth = _auth()
        payload = auth.verificar_token(auth.generar_token(_usuario(), amr=["pwd", "otp"]))
        assert payload["amr"] == ["pwd", "otp"]
