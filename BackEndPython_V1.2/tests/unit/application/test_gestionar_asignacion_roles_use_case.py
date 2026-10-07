from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.gestionar_asignacion_roles_use_case import (
    GestionarAsignacionRolesUseCase,
)
from src.domain.entities.rol_entity import RolEntity
from src.domain.entities.usuario_cuenta_entity import UsuarioCuentaEntity

_ADMIN_UID: int = 3
_OTRO_UID: int = 99
_RID_COMISIONISTA: int = 4
_RID_ADMIN: int = 3


def _repo_ok() -> AsyncMock:
    repo: AsyncMock = AsyncMock()
    repo.existe_rol_async.return_value = True
    repo.obtener_usuario_async.return_value = UsuarioCuentaEntity(
        uid=_OTRO_UID, nombre="pepe", email="pepe@x.co", activo=True
    )
    repo.obtener_nombre_rol_async.return_value = "comisionista"
    repo.asignar_rol_async.return_value = True
    repo.quitar_rol_async.return_value = True
    return repo


@pytest.mark.asyncio
async def test_asignar_rol_caso_feliz() -> None:
    repo: AsyncMock = _repo_ok()
    uc: GestionarAsignacionRolesUseCase = GestionarAsignacionRolesUseCase(repo)
    creado: bool = await uc.asignar_rol_async(_ADMIN_UID, _OTRO_UID, _RID_COMISIONISTA)
    assert creado is True
    repo.asignar_rol_async.assert_awaited_once_with(_OTRO_UID, _RID_COMISIONISTA)


@pytest.mark.asyncio
async def test_asignar_rol_tecnico_rechazado() -> None:
    repo: AsyncMock = _repo_ok()
    uc: GestionarAsignacionRolesUseCase = GestionarAsignacionRolesUseCase(repo)
    with pytest.raises(ValueError):
        await uc.asignar_rol_async(_ADMIN_UID, _OTRO_UID, 2)
    repo.asignar_rol_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_asignar_a_cuenta_sistema_rechazado() -> None:
    repo: AsyncMock = _repo_ok()
    uc: GestionarAsignacionRolesUseCase = GestionarAsignacionRolesUseCase(repo)
    with pytest.raises(ValueError):
        await uc.asignar_rol_async(_ADMIN_UID, 1, _RID_COMISIONISTA)
    repo.asignar_rol_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_asignar_rol_inexistente() -> None:
    repo: AsyncMock = _repo_ok()
    repo.existe_rol_async.return_value = False
    uc: GestionarAsignacionRolesUseCase = GestionarAsignacionRolesUseCase(repo)
    with pytest.raises(LookupError):
        await uc.asignar_rol_async(_ADMIN_UID, _OTRO_UID, 12345)


@pytest.mark.asyncio
async def test_asignar_usuario_inexistente() -> None:
    repo: AsyncMock = _repo_ok()
    repo.obtener_usuario_async.return_value = None
    uc: GestionarAsignacionRolesUseCase = GestionarAsignacionRolesUseCase(repo)
    with pytest.raises(LookupError):
        await uc.asignar_rol_async(_ADMIN_UID, _OTRO_UID, _RID_COMISIONISTA)


@pytest.mark.asyncio
async def test_quitar_propio_administrator_bloqueado() -> None:
    repo: AsyncMock = _repo_ok()
    repo.obtener_nombre_rol_async.return_value = "administrator"
    repo.obtener_usuario_async.return_value = UsuarioCuentaEntity(
        uid=_ADMIN_UID, nombre="admin", email="a@x.co", activo=True
    )
    uc: GestionarAsignacionRolesUseCase = GestionarAsignacionRolesUseCase(repo)
    with pytest.raises(ValueError):
        await uc.quitar_rol_async(_ADMIN_UID, _ADMIN_UID, _RID_ADMIN)
    repo.quitar_rol_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_quitar_administrator_de_otro_permitido() -> None:
    repo: AsyncMock = _repo_ok()
    repo.obtener_nombre_rol_async.return_value = "administrator"
    uc: GestionarAsignacionRolesUseCase = GestionarAsignacionRolesUseCase(repo)
    quitado: bool = await uc.quitar_rol_async(_ADMIN_UID, _OTRO_UID, _RID_ADMIN)
    assert quitado is True
    repo.quitar_rol_async.assert_awaited_once_with(_OTRO_UID, _RID_ADMIN)


@pytest.mark.asyncio
async def test_listar_usuarios_de_rol_tecnico_rechazado() -> None:
    repo: AsyncMock = _repo_ok()
    uc: GestionarAsignacionRolesUseCase = GestionarAsignacionRolesUseCase(repo)
    with pytest.raises(ValueError):
        await uc.listar_usuarios_de_rol_async(1, None, 1, 10)


@pytest.mark.asyncio
async def test_listar_roles_delega_en_repo() -> None:
    repo: AsyncMock = _repo_ok()
    repo.listar_roles_asignables_async.return_value = [RolEntity(rid=4, name="comisionista")]
    uc: GestionarAsignacionRolesUseCase = GestionarAsignacionRolesUseCase(repo)
    roles: list[RolEntity] = await uc.listar_roles_async()
    assert roles[0].name == "comisionista"
