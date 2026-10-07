from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from src.application.services.auth_service import AuthService
from src.application.services.login_throttle_service import LoginThrottleService
from src.application.services.servicio_expiracion_password import (
    ServicioExpiracionPassword,
)
from src.application.services.servicio_password_temporal import ServicioPasswordTemporal
from src.application.use_cases.cambiar_password_temporal_use_case import (
    CambiarPasswordTemporalUseCase,
)
from src.application.use_cases.login_use_case import LoginUseCase
from src.domain.entities.password_temporal_entity import PasswordTemporalEntity
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.credenciales_invalidas import CredencialesInvalidas
from src.domain.exceptions.password_insegura import PasswordInsegura
from src.domain.exceptions.password_temporal_requiere_cambio import (
    PasswordTemporalRequiereCambio,
)
from src.domain.exceptions.password_temporal_vencida import PasswordTemporalVencida
from src.domain.services.politica_expiracion_password import PoliticaExpiracionPassword
from src.domain.services.politica_password_temporal import PoliticaPasswordTemporal
from src.domain.value_objects.estado_password_temporal import EstadoPasswordTemporal
from src.domain.value_objects.origen_password_temporal import OrigenPasswordTemporal
from src.infrastructure.external.in_memory_estado_credencial_repo import (
    InMemoryEstadoCredencialRepo,
)
from src.infrastructure.external.in_memory_intentos_login_store import (
    InMemoryIntentosLoginStore,
)
from src.infrastructure.external.in_memory_password_expiracion_repo import (
    InMemoryPasswordExpiracionRepo,
)
from src.infrastructure.external.in_memory_password_history_repo import (
    InMemoryPasswordHistoryRepo,
)
from src.infrastructure.external.in_memory_password_temporal_repo import (
    InMemoryPasswordTemporalRepo,
)
from src.infrastructure.security.jwt_handler import JWTHandler
from src.infrastructure.security.password_hasher import PasswordHasher

SECRETO = "clave-de-pruebas-para-jwt-con-mas-de-veinte-caracteres"
AMBIGUOS = "0O1lI"


def _politica_temp(ttl_minutos: int = 120) -> PoliticaPasswordTemporal:
    return PoliticaPasswordTemporal(ttl_minutos=ttl_minutos)


def _servicio(
    repo: InMemoryPasswordTemporalRepo | None = None,
    habilitado: bool = True,
) -> tuple[ServicioPasswordTemporal, InMemoryPasswordTemporalRepo]:
    repo_real = repo if repo is not None else InMemoryPasswordTemporalRepo()
    servicio = ServicioPasswordTemporal(
        repo=repo_real,
        politica=_politica_temp(),
        hasher=PasswordHasher(),
        habilitado=habilitado,
    )
    return servicio, repo_real


def _auth() -> AuthService:
    return AuthService(JWTHandler(SECRETO, "HS256"), PasswordHasher(), 30)


def _entidad(expira_iso: str, estado: EstadoPasswordTemporal) -> PasswordTemporalEntity:
    return PasswordTemporalEntity(
        id=1,
        uid=1,
        hash_temporal="hash",
        emitida_por_uid=99,
        emitida_por_usuario="admin",
        origen=OrigenPasswordTemporal.ADMIN,
        emitida_iso="2026-07-03T10:00:00",
        expira_iso=expira_iso,
        estado=estado,
    )


class _FakeUsuarioRepo:
    def __init__(self, uid: int, hash_permanente: str) -> None:
        self._uid = uid
        self._hash = hash_permanente

    def _usuario(self) -> UsuarioEntity:
        return UsuarioEntity(
            uid=self._uid, nombre="usuario" + str(self._uid), email="x@y.co",
            roles=[], activo=True, new_pass_hash=self._hash,
        )

    async def obtener_por_nombre_async(self, nombre):
        return self._usuario()

    async def obtener_por_uid_async(self, uid):
        return self._usuario()

    async def actualizar_password_async(self, uid, nuevo_hash):
        self._hash = nuevo_hash


class _RepoSinUsuario:
    async def obtener_por_nombre_async(self, nombre):
        return None


class _RepoTemporalRoto:
    async def obtener_vigente(self, uid):
        raise RuntimeError("tabla inexistente")


class _FakeModulosRepo:
    async def obtener_modulos_por_uid_async(self, uid):
        return []


def _throttle() -> LoginThrottleService:
    return LoginThrottleService(
        store=InMemoryIntentosLoginStore(ttl_segundos=900),
        paso_segundos=5,
        maximo_segundos=30,
    )


class TestPoliticaTemporal:
    def test_limite_120_minutos_es_inclusivo(self):
        politica = _politica_temp()
        emitida = datetime(2026, 7, 3, 10, 0, 0)
        assert politica.calcular_expiracion(emitida) == datetime(2026, 7, 3, 12, 0, 0)
        entidad = _entidad("2026-07-03T12:00:00", EstadoPasswordTemporal.ACTIVA)
        assert politica.esta_vencida(entidad, datetime(2026, 7, 3, 12, 0, 0)) is False
        assert politica.esta_vencida(entidad, datetime(2026, 7, 3, 12, 0, 0, 1)) is True

    def test_consumida_no_puede_autenticar(self):
        politica = _politica_temp()
        entidad = _entidad("2026-07-03T12:00:00", EstadoPasswordTemporal.CONSUMIDA)
        assert politica.puede_autenticar(entidad, datetime(2026, 7, 3, 11, 0, 0)) is False

    def test_usada_vigente_puede_autenticar(self):
        politica = _politica_temp()
        entidad = _entidad("2026-07-03T12:00:00", EstadoPasswordTemporal.USADA)
        assert politica.puede_autenticar(entidad, datetime(2026, 7, 3, 11, 0, 0)) is True


class TestGeneradorClave:
    def test_longitud_clases_y_alfabeto(self):
        servicio, _ = _servicio()
        for _i in range(50):
            clave = servicio.generar_clave()
            assert len(clave) == 16
            assert not any(caracter in AMBIGUOS for caracter in clave)
            assert any(caracter.islower() for caracter in clave)
            assert any(caracter.isupper() for caracter in clave)
            assert any(caracter.isdigit() for caracter in clave)


class TestRepoTemporal:
    async def test_crear_reemplaza_la_vigente_previa(self):
        servicio, repo = _servicio()
        primera, _ = await servicio.emitir(1, 99, "admin", OrigenPasswordTemporal.ADMIN)
        segunda, _ = await servicio.emitir(1, 99, "admin", OrigenPasswordTemporal.ADMIN)
        vigente = await repo.obtener_vigente(1)
        assert vigente is not None
        assert vigente.id == segunda.id
        assert primera.id != segunda.id

    async def test_emitir_guarda_origen_completo(self):
        servicio, repo = _servicio()
        entidad, clave = await servicio.emitir(
            1, 99, "admin", OrigenPasswordTemporal.SOPORTE,
            motivo="ticket 4711", ip_emision="10.0.0.5",
        )
        assert entidad.emitida_por_uid == 99
        assert entidad.emitida_por_usuario == "admin"
        assert entidad.origen == OrigenPasswordTemporal.SOPORTE
        assert entidad.motivo == "ticket 4711"
        assert entidad.ip_emision == "10.0.0.5"
        assert PasswordHasher().verificar(clave, entidad.hash_temporal)


class TestVerificarLogin:
    async def test_match_vigente_lanza_y_estampa_primer_uso(self):
        servicio, repo = _servicio()
        usuario_repo = _FakeUsuarioRepo(1, PasswordHasher().hashear("Permanente#111"))
        entidad, clave = await servicio.emitir(1, 99, "admin", OrigenPasswordTemporal.ADMIN)
        with pytest.raises(PasswordTemporalRequiereCambio):
            await servicio.verificar_login("usuario1", clave, usuario_repo)
        vigente = await repo.obtener_vigente(1)
        assert vigente is not None
        assert vigente.estado == EstadoPasswordTemporal.USADA
        assert vigente.usada_iso is not None
        with pytest.raises(PasswordTemporalRequiereCambio):
            await servicio.verificar_login("usuario1", clave, usuario_repo)

    async def test_match_vencida_lanza_vencida(self):
        servicio, _repo = _servicio()
        usuario_repo = _FakeUsuarioRepo(1, PasswordHasher().hashear("Permanente#111"))
        pasado = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=3)
        _entidad_creada, clave = await servicio.emitir(
            1, 99, "admin", OrigenPasswordTemporal.ADMIN, ahora=pasado
        )
        with pytest.raises(PasswordTemporalVencida):
            await servicio.verificar_login("usuario1", clave, usuario_repo)

    async def test_sin_match_no_interfiere(self):
        servicio, _repo = _servicio()
        usuario_repo = _FakeUsuarioRepo(1, PasswordHasher().hashear("Permanente#111"))
        await servicio.emitir(1, 99, "admin", OrigenPasswordTemporal.ADMIN)
        assert await servicio.verificar_login("usuario1", "OtraClave#999", usuario_repo) is None

    async def test_usuario_inexistente_no_interfiere(self):
        servicio, _repo = _servicio()
        assert await servicio.verificar_login("nadie", "Clave#12345678", _RepoSinUsuario()) is None

    async def test_fail_safe_con_repo_roto(self):
        servicio = ServicioPasswordTemporal(
            repo=_RepoTemporalRoto(),
            politica=_politica_temp(),
            hasher=PasswordHasher(),
        )
        usuario_repo = _FakeUsuarioRepo(1, PasswordHasher().hashear("Permanente#111"))
        assert await servicio.verificar_login("usuario1", "Clave#12345678", usuario_repo) is None

    async def test_deshabilitado_no_interfiere(self):
        servicio, _repo = _servicio(habilitado=False)
        usuario_repo = _FakeUsuarioRepo(1, PasswordHasher().hashear("Permanente#111"))
        assert await servicio.verificar_login("usuario1", "Clave#12345678", usuario_repo) is None


def _uc_cambio(
    servicio: ServicioPasswordTemporal,
    usuario_repo: _FakeUsuarioRepo,
    expiracion_repo: InMemoryPasswordExpiracionRepo,
    historial: InMemoryPasswordHistoryRepo,
    estado: InMemoryEstadoCredencialRepo,
) -> CambiarPasswordTemporalUseCase:
    async def _sin_espera(_segundos: float) -> None:
        return None

    expiracion = ServicioExpiracionPassword(
        repo=expiracion_repo,
        politica=PoliticaExpiracionPassword(vigencia_dias=45, aviso_dias=7, gracia_dias=5),
    )
    return CambiarPasswordTemporalUseCase(
        auth_service=_auth(),
        usuario_repo=usuario_repo,
        modulos_repo=_FakeModulosRepo(),
        servicio_temporal=servicio,
        expiracion=expiracion,
        throttle=_throttle(),
        sleeper=_sin_espera,
        estado_credencial=estado,
        historial=historial,
        historial_tamano=24,
    )


class TestCambioObligatorio:
    async def test_cambio_feliz_consume_y_emite_sesion(self):
        hasher = PasswordHasher()
        servicio, repo = _servicio()
        usuario_repo = _FakeUsuarioRepo(1, hasher.hashear("Permanente#111"))
        expiracion_repo = InMemoryPasswordExpiracionRepo()
        historial = InMemoryPasswordHistoryRepo()
        estado = InMemoryEstadoCredencialRepo()
        _entidad_creada, clave = await servicio.emitir(
            1, 99, "admin", OrigenPasswordTemporal.ADMIN
        )
        uc = _uc_cambio(servicio, usuario_repo, expiracion_repo, historial, estado)
        result = await uc.ejecutar_async("usuario1", clave, "NuevaClave#333", "k")
        assert result.token
        assert hasher.verificar("NuevaClave#333", usuario_repo._hash)
        assert await repo.obtener_vigente(1) is None
        assert await expiracion_repo.obtener_cambiado_en(1) is not None
        archivadas = await historial.ultimos_hashes(1, 24)
        assert len(archivadas) == 1
        assert hasher.verificar("Permanente#111", archivadas[0])
        assert await estado.obtener_version(1) == 2

    async def test_nueva_igual_a_la_temporal_rechazada(self):
        servicio, _repo = _servicio()
        usuario_repo = _FakeUsuarioRepo(1, PasswordHasher().hashear("Permanente#111"))
        _entidad_creada, clave = await servicio.emitir(
            1, 99, "admin", OrigenPasswordTemporal.ADMIN
        )
        uc = _uc_cambio(
            servicio, usuario_repo, InMemoryPasswordExpiracionRepo(),
            InMemoryPasswordHistoryRepo(), InMemoryEstadoCredencialRepo(),
        )
        with pytest.raises(PasswordInsegura):
            await uc.ejecutar_async("usuario1", clave, clave, "k")

    async def test_temporal_incorrecta_es_generica(self):
        servicio, _repo = _servicio()
        usuario_repo = _FakeUsuarioRepo(1, PasswordHasher().hashear("Permanente#111"))
        await servicio.emitir(1, 99, "admin", OrigenPasswordTemporal.ADMIN)
        uc = _uc_cambio(
            servicio, usuario_repo, InMemoryPasswordExpiracionRepo(),
            InMemoryPasswordHistoryRepo(), InMemoryEstadoCredencialRepo(),
        )
        with pytest.raises(CredencialesInvalidas):
            await uc.ejecutar_async("usuario1", "Incorrecta#999", "NuevaClave#333", "k")

    async def test_temporal_consumida_no_se_reutiliza(self):
        servicio, _repo = _servicio()
        usuario_repo = _FakeUsuarioRepo(1, PasswordHasher().hashear("Permanente#111"))
        _entidad_creada, clave = await servicio.emitir(
            1, 99, "admin", OrigenPasswordTemporal.ADMIN
        )
        uc = _uc_cambio(
            servicio, usuario_repo, InMemoryPasswordExpiracionRepo(),
            InMemoryPasswordHistoryRepo(), InMemoryEstadoCredencialRepo(),
        )
        await uc.ejecutar_async("usuario1", clave, "NuevaClave#333", "k")
        with pytest.raises(CredencialesInvalidas):
            await uc.ejecutar_async("usuario1", clave, "OtraClave#444", "k")

    async def test_temporal_vencida_pide_reemision(self):
        servicio, _repo = _servicio()
        usuario_repo = _FakeUsuarioRepo(1, PasswordHasher().hashear("Permanente#111"))
        pasado = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=3)
        _entidad_creada, clave = await servicio.emitir(
            1, 99, "admin", OrigenPasswordTemporal.ADMIN, ahora=pasado
        )
        uc = _uc_cambio(
            servicio, usuario_repo, InMemoryPasswordExpiracionRepo(),
            InMemoryPasswordHistoryRepo(), InMemoryEstadoCredencialRepo(),
        )
        with pytest.raises(PasswordTemporalVencida):
            await uc.ejecutar_async("usuario1", clave, "NuevaClave#333", "k")

    async def test_sin_credencial_permanente_previa(self):
        # Provision inicial: usuario sin new_pass utilizable; la temporal es la unica puerta.
        hasher = PasswordHasher()
        servicio, repo = _servicio()
        usuario_repo = _FakeUsuarioRepo(1, "")
        historial = InMemoryPasswordHistoryRepo()
        _entidad_creada, clave = await servicio.emitir(
            1, 99, "admin", OrigenPasswordTemporal.SISTEMA
        )
        uc = _uc_cambio(
            servicio, usuario_repo, InMemoryPasswordExpiracionRepo(),
            historial, InMemoryEstadoCredencialRepo(),
        )
        result = await uc.ejecutar_async("usuario1", clave, "NuevaClave#333", "k")
        assert result.token
        assert hasher.verificar("NuevaClave#333", usuario_repo._hash)
        assert await historial.ultimos_hashes(1, 24) == []
        assert await repo.obtener_vigente(1) is None


class TestLoginConTemporal:
    def _login_uc(
        self,
        usuario_repo,
        servicio: ServicioPasswordTemporal | None,
    ) -> tuple[LoginUseCase, list[float]]:
        dormido: list[float] = []

        async def _sleeper(segundos: float) -> None:
            dormido.append(segundos)

        uc = LoginUseCase(
            auth_service=_auth(),
            throttle=_throttle(),
            usuario_repo=usuario_repo,
            modulos_repo=_FakeModulosRepo(),
            sleeper=_sleeper,
            password_temporal=servicio,
        )
        return uc, dormido

    async def test_login_con_temporal_lanza_409_sin_contar_fallo(self):
        servicio, repo = _servicio()
        usuario_repo = _FakeUsuarioRepo(1, PasswordHasher().hashear("Permanente#111"))
        _entidad_creada, clave = await servicio.emitir(
            1, 99, "admin", OrigenPasswordTemporal.ADMIN
        )
        uc, dormido = self._login_uc(usuario_repo, servicio)
        with pytest.raises(PasswordTemporalRequiereCambio):
            await uc.ejecutar_async("usuario1", clave, "ip|usuario1")
        assert dormido == []
        vigente = await repo.obtener_vigente(1)
        assert vigente is not None
        assert vigente.estado == EstadoPasswordTemporal.USADA

    async def test_login_normal_sigue_intacto_sin_temporal(self):
        servicio, _repo = _servicio()
        usuario_repo = _FakeUsuarioRepo(1, PasswordHasher().hashear("Permanente#111"))
        uc, dormido = self._login_uc(usuario_repo, servicio)
        with pytest.raises(CredencialesInvalidas):
            await uc.ejecutar_async("usuario1", "Incorrecta#999", "ip|usuario1")
        assert dormido == [5]

    async def test_login_con_permanente_correcta_no_toca_temporal(self):
        servicio, repo = _servicio()
        usuario_repo = _FakeUsuarioRepo(1, PasswordHasher().hashear("Permanente#111"))
        await servicio.emitir(1, 99, "admin", OrigenPasswordTemporal.ADMIN)
        uc, _dormido = self._login_uc(usuario_repo, servicio)
        result = await uc.ejecutar_async("usuario1", "Permanente#111", "ip|usuario1")
        assert result.token
        vigente = await repo.obtener_vigente(1)
        assert vigente is not None
        assert vigente.estado == EstadoPasswordTemporal.ACTIVA
