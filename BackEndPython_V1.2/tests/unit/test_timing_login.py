from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.services.auth_service import AuthService
from src.domain.entities.usuario_entity import UsuarioEntity


def _make_auth(hasher: MagicMock) -> AuthService:
    return AuthService(
        jwt_handler=MagicMock(),
        password_hasher=hasher,
        jwt_expire_minutes=30,
        crypto_sapin=None,
    )


def _usuario(new_pass_hash: str | None = None) -> UsuarioEntity:
    return UsuarioEntity(uid=1, nombre="user1", email="u@x.com", new_pass_hash=new_pass_hash)


class TestTimingEqualizacion:
    # AP-0160: bcrypt se ejecuta siempre, independiente de si el usuario existe.

    @pytest.mark.asyncio
    async def test_usuario_inexistente_llama_verificar_dummy(self) -> None:
        repo: AsyncMock = AsyncMock()
        repo.obtener_por_nombre_async.return_value = None
        hasher: MagicMock = MagicMock()
        result = await _make_auth(hasher).autenticar_async("noexiste", "Password1!", repo)
        assert result is None
        hasher.verificar_dummy.assert_called_once_with("Password1!")
        hasher.verificar.assert_not_called()

    @pytest.mark.asyncio
    async def test_usuario_sin_hash_llama_verificar_dummy(self) -> None:
        repo: AsyncMock = AsyncMock()
        repo.obtener_por_nombre_async.return_value = _usuario(new_pass_hash=None)
        hasher: MagicMock = MagicMock()
        result = await _make_auth(hasher).autenticar_async("user1", "Password1!", repo)
        assert result is None
        hasher.verificar_dummy.assert_called_once()
        hasher.verificar.assert_not_called()

    @pytest.mark.asyncio
    async def test_usuario_existente_pwd_correcta_llama_verificar_real(self) -> None:
        repo: AsyncMock = AsyncMock()
        usuario = _usuario(new_pass_hash="$2b$12$hash_valido")
        repo.obtener_por_nombre_async.return_value = usuario
        hasher: MagicMock = MagicMock()
        hasher.verificar.return_value = True
        result = await _make_auth(hasher).autenticar_async("user1", "Password1!", repo)
        assert result == usuario
        hasher.verificar.assert_called_once_with("Password1!", "$2b$12$hash_valido")
        hasher.verificar_dummy.assert_not_called()

    @pytest.mark.asyncio
    async def test_usuario_existente_pwd_errada_llama_verificar_real(self) -> None:
        repo: AsyncMock = AsyncMock()
        repo.obtener_por_nombre_async.return_value = _usuario(new_pass_hash="$2b$12$hash")
        hasher: MagicMock = MagicMock()
        hasher.verificar.return_value = False
        result = await _make_auth(hasher).autenticar_async("user1", "wrongpass", repo)
        assert result is None
        hasher.verificar.assert_called_once()
        hasher.verificar_dummy.assert_not_called()

    @pytest.mark.asyncio
    async def test_usuario_inexistente_siempre_retorna_none(self) -> None:
        repo: AsyncMock = AsyncMock()
        repo.obtener_por_nombre_async.return_value = None
        result = await _make_auth(MagicMock()).autenticar_async("fantasma", "cualquier", repo)
        assert result is None
