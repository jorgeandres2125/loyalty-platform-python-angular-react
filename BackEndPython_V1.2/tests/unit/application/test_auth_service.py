"""Tests para AuthService (JWT + bcrypt). Sin claim 'permisos' (legacy)."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.application.services.auth_service import AuthService
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.credenciales_invalidas import CredencialesInvalidas
from src.domain.value_objects.rol_usuario import RolUsuario
from src.infrastructure.security.jwt_handler import JWTHandler
from src.infrastructure.security.password_hasher import PasswordHasher


@pytest.fixture
def auth_service() -> AuthService:
    return AuthService(
        jwt_handler=JWTHandler(secret_key="test-secret-key-min-32-chars-xxxxx", algorithm="HS256"),
        password_hasher=PasswordHasher(),
        jwt_expire_minutes=60,
    )


def _usuario(uid: int = 1, password: str = "Admin2024*", roles: list[RolUsuario] | None = None) -> UsuarioEntity:
    return UsuarioEntity(
        uid=uid,
        nombre=str(uid),
        email="x@y.co",
        roles=roles or [RolUsuario.COMISIONISTA],
        activo=True,
        new_pass_hash=PasswordHasher().hashear(password),
    )


# ── Token ───────────────────────────────────────────────────────────────────

def test_generar_token_no_contiene_claim_permisos(auth_service: AuthService) -> None:
    """El JWT solo lleva sub, nombre y roles — no 'permisos' (eliminado 2026-05-19)."""
    token = auth_service.generar_token(_usuario())
    payload = auth_service.verificar_token(token)
    assert "permisos" not in payload


def test_generar_token_contiene_sub_nombre_roles(auth_service: AuthService) -> None:
    token = auth_service.generar_token(_usuario(uid=42, roles=[RolUsuario.COMISIONISTA_CONSUMO]))
    payload = auth_service.verificar_token(token)
    assert payload["sub"] == "42"
    assert payload["nombre"] == "42"
    assert payload["roles"] == ["comisionista_consumo"]


def test_generar_token_roles_son_slug_con_underscore(auth_service: AuthService) -> None:
    """Los roles en el JWT son RolUsuario.value (slug), no el legacy con espacios."""
    token = auth_service.generar_token(_usuario(roles=[RolUsuario.COMISIONISTA_CONSUMO]))
    payload = auth_service.verificar_token(token)
    assert "comisionista_consumo" in payload["roles"]
    assert "comisionista consumo" not in payload["roles"]


# ── Autenticación ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_autenticar_password_correcta_retorna_usuario(auth_service: AuthService) -> None:
    repo = AsyncMock()
    repo.obtener_por_nombre_async.return_value = _usuario(password="Admin2024*")
    u = await auth_service.autenticar_async("1", "Admin2024*", repo)
    assert u is not None
    assert u.uid == 1


@pytest.mark.asyncio
async def test_autenticar_password_incorrecta_retorna_none(auth_service: AuthService) -> None:
    repo = AsyncMock()
    repo.obtener_por_nombre_async.return_value = _usuario(password="Admin2024*")
    assert await auth_service.autenticar_async("1", "wrong", repo) is None


@pytest.mark.asyncio
async def test_autenticar_usuario_inexistente_retorna_none(auth_service: AuthService) -> None:
    repo = AsyncMock()
    repo.obtener_por_nombre_async.return_value = None
    assert await auth_service.autenticar_async("999", "Admin2024*", repo) is None


@pytest.mark.asyncio
async def test_autenticar_sin_new_pass_retorna_none(auth_service: AuthService) -> None:
    """Usuarios legacy sin bcrypt no pueden loguear (pass es read-only)."""
    repo = AsyncMock()
    u = UsuarioEntity(uid=1, nombre="1", email="x@y.co", roles=[], activo=True, new_pass_hash=None)
    repo.obtener_por_nombre_async.return_value = u
    assert await auth_service.autenticar_async("1", "Admin2024*", repo) is None


# ── Cambio de contraseña con re-autenticación (AP-0020) ──────────────────────


@pytest.mark.asyncio
async def test_cambiar_password_con_actual_correcta_actualiza(auth_service: AuthService) -> None:
    repo = AsyncMock()
    repo.obtener_por_uid_async.return_value = _usuario(uid=7, password="Actual2024*")
    await auth_service.cambiar_password_async(7, "Actual2024*", "Nueva2025*", repo)
    repo.actualizar_password_async.assert_awaited_once()
    uid_arg, hash_arg = repo.actualizar_password_async.await_args.args
    assert uid_arg == 7
    assert hash_arg != "Nueva2025*"  # se guarda el hash bcrypt, no el texto plano


@pytest.mark.asyncio
async def test_cambiar_password_con_actual_incorrecta_falla(auth_service: AuthService) -> None:
    repo = AsyncMock()
    repo.obtener_por_uid_async.return_value = _usuario(uid=7, password="Actual2024*")
    with pytest.raises(CredencialesInvalidas):
        await auth_service.cambiar_password_async(7, "OtraCosa*", "Nueva2025*", repo)
    repo.actualizar_password_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_cambiar_password_usuario_inexistente_falla(auth_service: AuthService) -> None:
    repo = AsyncMock()
    repo.obtener_por_uid_async.return_value = None
    with pytest.raises(CredencialesInvalidas):
        await auth_service.cambiar_password_async(99, "loquesea", "Nueva2025*", repo)
    repo.actualizar_password_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_cambiar_password_sin_new_pass_falla(auth_service: AuthService) -> None:
    """Sin bcrypt no se puede re-autenticar → no se permite la novedad."""
    repo = AsyncMock()
    repo.obtener_por_uid_async.return_value = UsuarioEntity(
        uid=7, nombre="7", email="x@y.co", roles=[], activo=True, new_pass_hash=None
    )
    with pytest.raises(CredencialesInvalidas):
        await auth_service.cambiar_password_async(7, "loquesea", "Nueva2025*", repo)
    repo.actualizar_password_async.assert_not_awaited()
