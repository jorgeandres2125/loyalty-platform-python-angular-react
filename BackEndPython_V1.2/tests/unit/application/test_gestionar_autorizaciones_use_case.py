"""Tests para GestionarAutorizacionesUseCase (parametrización de autorizaciones, AP-0054)."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.gestionar_autorizaciones_use_case import (
    GestionarAutorizacionesUseCase,
)
from src.domain.entities.autorizacion_modulo_entity import AutorizacionModuloEntity
from src.domain.entities.rol_entity import RolEntity
from src.domain.value_objects.permisos_modulo import PermisosModulo


def _make_uc(
    roles: list[RolEntity] | None = None,
    matriz: list[AutorizacionModuloEntity] | None = None,
    actualizado: AutorizacionModuloEntity | None = None,
) -> tuple[GestionarAutorizacionesUseCase, AsyncMock]:
    repo = AsyncMock()
    repo.listar_roles_async.return_value = roles or []
    repo.obtener_matriz_por_rol_async.return_value = matriz or []
    repo.actualizar_permisos_async.return_value = actualizado
    return GestionarAutorizacionesUseCase(autorizaciones_repo=repo), repo


@pytest.mark.asyncio
async def test_listar_roles_delega_en_repo() -> None:
    uc, repo = _make_uc(roles=[RolEntity(rid=3, name="administrator")])
    roles = await uc.listar_roles_async()
    assert roles[0].name == "administrator"
    repo.listar_roles_async.assert_awaited_once()


@pytest.mark.asyncio
async def test_obtener_matriz_delega_en_repo() -> None:
    fila = AutorizacionModuloEntity(
        rid=3, module_id=1, module_code="DASHBOARD", module_nombre="Dashboard"
    )
    uc, repo = _make_uc(matriz=[fila])
    matriz = await uc.obtener_matriz_async(3)
    assert matriz[0].module_code == "DASHBOARD"
    repo.obtener_matriz_por_rol_async.assert_awaited_once_with(3)


@pytest.mark.asyncio
async def test_actualizar_permisos_persiste_flags_validos() -> None:
    resultado = AutorizacionModuloEntity(
        rid=3, module_id=1, module_code="REPORTES", module_nombre="Reportes",
        puede_ver=True, puede_exportar=True,
    )
    uc, repo = _make_uc(actualizado=resultado)
    flags = PermisosModulo(puede_ver=True, puede_exportar=True)
    entity = await uc.actualizar_permisos_async(3, 1, flags)
    assert entity is not None and entity.puede_exportar is True
    repo.actualizar_permisos_async.assert_awaited_once_with(3, 1, flags)


@pytest.mark.asyncio
async def test_actualizar_permisos_rechaza_accion_sin_ver() -> None:
    """AP-0054: no se puede otorgar una acción sin 'puede_ver' (estado incoherente)."""
    uc, repo = _make_uc()
    flags = PermisosModulo(puede_ver=False, puede_editar=True)
    with pytest.raises(ValueError):
        await uc.actualizar_permisos_async(3, 1, flags)
    repo.actualizar_permisos_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_actualizar_permisos_modulo_inexistente_retorna_none() -> None:
    uc, _ = _make_uc(actualizado=None)
    flags = PermisosModulo(puede_ver=True)
    assert await uc.actualizar_permisos_async(3, 999, flags) is None
