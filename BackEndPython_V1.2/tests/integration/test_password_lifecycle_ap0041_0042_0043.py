from __future__ import annotations

from datetime import datetime

import pytest

from src.application.services.auth_service import AuthService
from src.application.services.servicio_expiracion_password import (
    ServicioExpiracionPassword,
)
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.password_reutilizada import PasswordReutilizada
from src.domain.services.politica_expiracion_password import PoliticaExpiracionPassword
from src.infrastructure.external.in_memory_password_expiracion_repo import (
    InMemoryPasswordExpiracionRepo,
)
from src.infrastructure.external.in_memory_password_history_repo import (
    InMemoryPasswordHistoryRepo,
)
from src.infrastructure.security.jwt_handler import JWTHandler
from src.infrastructure.security.password_hasher import PasswordHasher

TZ = "America/Bogota"
SECRETO = "clave-de-pruebas-para-jwt-con-mas-de-veinte-caracteres"


def _politica() -> PoliticaExpiracionPassword:
    return PoliticaExpiracionPassword(vigencia_dias=45, aviso_dias=7, gracia_dias=5)


class TestMismoDia:
    def test_mismo_dia_local(self):
        cambiado = datetime(2026, 7, 3, 13, 0, 0)  # 08:00 Bogota, 3 jul
        ahora = datetime(2026, 7, 3, 20, 0, 0)  # 15:00 Bogota, 3 jul
        assert _politica().es_mismo_dia_local(cambiado, ahora, TZ) is True

    def test_distinto_dia(self):
        cambiado = datetime(2026, 7, 2, 20, 0, 0)  # 15:00 Bogota, 2 jul
        ahora = datetime(2026, 7, 3, 20, 0, 0)  # 15:00 Bogota, 3 jul
        assert _politica().es_mismo_dia_local(cambiado, ahora, TZ) is False

    def test_borde_utc_mismo_dia_pero_distinto_local(self):
        cambiado = datetime(2026, 7, 3, 2, 0, 0)  # 21:00 Bogota del 2 jul
        ahora = datetime(2026, 7, 3, 10, 0, 0)  # 05:00 Bogota del 3 jul
        assert _politica().es_mismo_dia_local(cambiado, ahora, TZ) is False


class TestCambiadaHoy:
    async def test_sin_baseline_false(self):
        servicio = ServicioExpiracionPassword(
            repo=InMemoryPasswordExpiracionRepo(), politica=_politica()
        )
        assert await servicio.cambiada_hoy(1, TZ, datetime(2026, 7, 3, 20, 0, 0)) is False

    async def test_cambiada_hoy_true(self):
        repo = InMemoryPasswordExpiracionRepo()
        await repo.registrar_cambio(1, datetime(2026, 7, 3, 13, 0, 0))
        servicio = ServicioExpiracionPassword(repo=repo, politica=_politica())
        assert await servicio.cambiada_hoy(1, TZ, datetime(2026, 7, 3, 20, 0, 0)) is True

    async def test_cambiada_ayer_false(self):
        repo = InMemoryPasswordExpiracionRepo()
        await repo.registrar_cambio(1, datetime(2026, 7, 2, 20, 0, 0))
        servicio = ServicioExpiracionPassword(repo=repo, politica=_politica())
        assert await servicio.cambiada_hoy(1, TZ, datetime(2026, 7, 3, 20, 0, 0)) is False


class TestHistorialRepo:
    async def test_insertar_y_ultimos_orden_desc(self):
        repo = InMemoryPasswordHistoryRepo()
        await repo.insertar(1, "hA", "2026-07-01T10:00:00")
        await repo.insertar(1, "hB", "2026-07-02T10:00:00")
        await repo.insertar(1, "hC", "2026-07-03T10:00:00")
        assert await repo.ultimos_hashes(1, 24) == ["hC", "hB", "hA"]

    async def test_podar_conserva_los_mas_recientes(self):
        repo = InMemoryPasswordHistoryRepo()
        for indice in range(5):
            await repo.insertar(1, "h" + str(indice), "2026-07-0" + str(indice + 1) + "T10:00:00")
        await repo.podar(1, 2)
        assert await repo.ultimos_hashes(1, 24) == ["h4", "h3"]

    async def test_solo_del_usuario(self):
        repo = InMemoryPasswordHistoryRepo()
        await repo.insertar(1, "h1", "2026-07-01T10:00:00")
        await repo.insertar(2, "h2", "2026-07-01T10:00:00")
        assert await repo.ultimos_hashes(1, 24) == ["h1"]


class _FakeUsuarioRepo:
    def __init__(self, uid: int, hash_actual: str) -> None:
        self._uid = uid
        self._hash = hash_actual

    async def obtener_por_uid_async(self, uid):
        return UsuarioEntity(
            uid=self._uid, nombre=str(self._uid), email="x@y.co", roles=[],
            activo=True, new_pass_hash=self._hash,
        )

    async def obtener_por_nombre_async(self, nombre):
        return None

    async def actualizar_password_async(self, uid, nuevo_hash):
        self._hash = nuevo_hash


def _auth() -> AuthService:
    return AuthService(JWTHandler(SECRETO, "HS256"), PasswordHasher(), 30)


class TestReutilizacion:
    async def test_no_reusar_la_actual(self):
        hasher = PasswordHasher()
        repo = _FakeUsuarioRepo(1, hasher.hashear("ClaveAaa#111"))
        hist = InMemoryPasswordHistoryRepo()
        with pytest.raises(PasswordReutilizada):
            await _auth().cambiar_password_async(
                1, "ClaveAaa#111", "ClaveAaa#111", repo, historial=hist, historial_tamano=24
            )

    async def test_cambio_unico_archiva_la_anterior(self):
        hasher = PasswordHasher()
        repo = _FakeUsuarioRepo(1, hasher.hashear("ClaveAaa#111"))
        hist = InMemoryPasswordHistoryRepo()
        await _auth().cambiar_password_async(
            1, "ClaveAaa#111", "ClaveBbb#222", repo, historial=hist, historial_tamano=24
        )
        archivadas = await hist.ultimos_hashes(1, 24)
        assert len(archivadas) == 1
        assert hasher.verificar("ClaveAaa#111", archivadas[0])

    async def test_no_reusar_una_archivada(self):
        hasher = PasswordHasher()
        repo = _FakeUsuarioRepo(1, hasher.hashear("ClaveAaa#111"))
        hist = InMemoryPasswordHistoryRepo()
        auth = _auth()
        await auth.cambiar_password_async(
            1, "ClaveAaa#111", "ClaveBbb#222", repo, historial=hist, historial_tamano=24
        )
        with pytest.raises(PasswordReutilizada):
            await auth.cambiar_password_async(
                1, "ClaveBbb#222", "ClaveAaa#111", repo, historial=hist, historial_tamano=24
            )

    async def test_password_totalmente_nueva_ok(self):
        hasher = PasswordHasher()
        repo = _FakeUsuarioRepo(1, hasher.hashear("ClaveAaa#111"))
        hist = InMemoryPasswordHistoryRepo()
        auth = _auth()
        await auth.cambiar_password_async(
            1, "ClaveAaa#111", "ClaveBbb#222", repo, historial=hist, historial_tamano=24
        )
        await auth.cambiar_password_async(
            1, "ClaveBbb#222", "ClaveCcc#333", repo, historial=hist, historial_tamano=24
        )

    async def test_sin_historial_no_valida_reuso(self):
        hasher = PasswordHasher()
        repo = _FakeUsuarioRepo(1, hasher.hashear("ClaveAaa#111"))
        await _auth().cambiar_password_async(1, "ClaveAaa#111", "ClaveAaa#111", repo)
