"""Tests para GestionarUsuariosUseCase (AP-0001: deshabilitar/habilitar cuentas).

Cubre la matriz de autorización quién-puede-sobre-quién y las guardias de negocio
(auto-bloqueo, cuentas del sistema, resolución por documento). No requiere BD:
el repositorio se sustituye por un AsyncMock.
"""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.gestionar_usuarios_use_case import GestionarUsuariosUseCase
from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.exceptions.permiso_denegado import PermisoDenegado
from src.domain.value_objects.rol_usuario import RolUsuario


def _usuario(
    uid: int,
    roles: list[RolUsuario] | None = None,
    activo: bool = True,
) -> UsuarioEntity:
    return UsuarioEntity(
        uid=uid,
        nombre=str(uid),
        email=f"u{uid}@sufi.co",
        roles=roles or [],
        activo=activo,
    )


def _make_uc(
    objetivo: UsuarioEntity | None = None,
    uid_por_documento: int | None = None,
    listar: tuple[list[UsuarioEntity], int] | None = None,
) -> tuple[GestionarUsuariosUseCase, AsyncMock]:
    repo = AsyncMock()
    repo.obtener_cualquiera_por_uid_async.return_value = objetivo
    repo.obtener_uid_por_documento_async.return_value = uid_por_documento
    repo.listar_paginado_async.return_value = listar or ([], 0)
    repo.actualizar_estado_async.return_value = None
    return GestionarUsuariosUseCase(usuario_repo=repo), repo


_ADMIN: list[RolUsuario] = [RolUsuario.ADMINISTRATOR]
_ASESOR: list[RolUsuario] = [RolUsuario.ASESOR_CONSUMO]


# ── happy path admin ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_deshabilita_comisionista() -> None:
    objetivo = _usuario(700, [RolUsuario.COMISIONISTA], activo=True)
    uc, repo = _make_uc(objetivo=objetivo)
    resultado = await uc.cambiar_estado_async(700, activo=False, actor_uid=10, actor_roles=_ADMIN)
    assert resultado.activo is False
    repo.actualizar_estado_async.assert_awaited_once_with(700, False)


@pytest.mark.asyncio
async def test_admin_rehabilita_comisionista() -> None:
    objetivo = _usuario(700, [RolUsuario.COMISIONISTA], activo=False)
    uc, repo = _make_uc(objetivo=objetivo)
    resultado = await uc.cambiar_estado_async(700, activo=True, actor_uid=10, actor_roles=_ADMIN)
    assert resultado.activo is True
    repo.actualizar_estado_async.assert_awaited_once_with(700, True)


# ── guardias de negocio ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_no_puede_deshabilitar_su_propia_cuenta() -> None:
    uc, repo = _make_uc(objetivo=_usuario(10, _ADMIN))
    with pytest.raises(ValueError, match="propia cuenta"):
        await uc.cambiar_estado_async(10, activo=False, actor_uid=10, actor_roles=_ADMIN)
    repo.actualizar_estado_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_puede_rehabilitarse_a_si_mismo() -> None:
    # rehabilitar (activo=True) la propia cuenta no es auto-bloqueo
    uc, repo = _make_uc(objetivo=_usuario(10, _ADMIN, activo=False))
    resultado = await uc.cambiar_estado_async(10, activo=True, actor_uid=10, actor_roles=_ADMIN)
    assert resultado.activo is True


@pytest.mark.asyncio
@pytest.mark.parametrize("uid_sistema", [0, 1])
async def test_no_puede_tocar_cuentas_del_sistema(uid_sistema: int) -> None:
    uc, repo = _make_uc()
    with pytest.raises(ValueError, match="cuenta del sistema"):
        await uc.cambiar_estado_async(uid_sistema, activo=False, actor_uid=10, actor_roles=_ADMIN)
    repo.obtener_cualquiera_por_uid_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_usuario_inexistente_lanza_lookup_error() -> None:
    uc, _ = _make_uc(objetivo=None)
    with pytest.raises(LookupError):
        await uc.cambiar_estado_async(999, activo=False, actor_uid=10, actor_roles=_ADMIN)


@pytest.mark.asyncio
async def test_admin_no_puede_deshabilitar_a_otro_admin() -> None:
    uc, repo = _make_uc(objetivo=_usuario(20, [RolUsuario.ADMINISTRATOR]))
    with pytest.raises(ValueError, match="otro administrador"):
        await uc.cambiar_estado_async(20, activo=False, actor_uid=10, actor_roles=_ADMIN)
    repo.actualizar_estado_async.assert_not_awaited()


# ── alcance del actor asesor ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_asesor_deshabilita_comisionista_ok() -> None:
    objetivo = _usuario(700, [RolUsuario.COMISIONISTA_CONSUMO])
    uc, repo = _make_uc(objetivo=objetivo)
    resultado = await uc.cambiar_estado_async(700, activo=False, actor_uid=30, actor_roles=_ASESOR)
    assert resultado.activo is False
    repo.actualizar_estado_async.assert_awaited_once_with(700, False)


@pytest.mark.asyncio
async def test_asesor_no_puede_deshabilitar_staff() -> None:
    uc, repo = _make_uc(objetivo=_usuario(40, [RolUsuario.DOCUMENTADOR]))
    with pytest.raises(PermisoDenegado):
        await uc.cambiar_estado_async(40, activo=False, actor_uid=30, actor_roles=_ASESOR)
    repo.actualizar_estado_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_asesor_no_puede_deshabilitar_cuenta_con_roles_mixtos() -> None:
    # comisionista + rol staff → no es exclusivamente comisionista → denegado
    objetivo = _usuario(50, [RolUsuario.COMISIONISTA, RolUsuario.ASESOR_COMERCIAL])
    uc, repo = _make_uc(objetivo=objetivo)
    with pytest.raises(PermisoDenegado):
        await uc.cambiar_estado_async(50, activo=False, actor_uid=30, actor_roles=_ASESOR)


@pytest.mark.asyncio
async def test_asesor_no_puede_deshabilitar_cuenta_sin_roles() -> None:
    uc, _ = _make_uc(objetivo=_usuario(60, roles=[]))
    with pytest.raises(PermisoDenegado):
        await uc.cambiar_estado_async(60, activo=False, actor_uid=30, actor_roles=_ASESOR)


# ── resolución por documento (superficie asesor) ─────────────────────────────

@pytest.mark.asyncio
async def test_cambiar_estado_por_documento_resuelve_uid() -> None:
    objetivo = _usuario(700, [RolUsuario.COMISIONISTA])
    uc, repo = _make_uc(objetivo=objetivo, uid_por_documento=700)
    resultado = await uc.cambiar_estado_por_documento_async(
        "1129565843", activo=False, actor_uid=30, actor_roles=_ASESOR
    )
    assert resultado.activo is False
    repo.obtener_uid_por_documento_async.assert_awaited_once_with("1129565843")
    repo.actualizar_estado_async.assert_awaited_once_with(700, False)


@pytest.mark.asyncio
async def test_cambiar_estado_por_documento_sin_cuenta_lanza_lookup() -> None:
    uc, repo = _make_uc(uid_por_documento=None)
    with pytest.raises(LookupError, match="cuenta de acceso"):
        await uc.cambiar_estado_por_documento_async(
            "0000", activo=False, actor_uid=30, actor_roles=_ASESOR
        )
    repo.obtener_cualquiera_por_uid_async.assert_not_awaited()


# ── listado ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_listar_mapea_dto() -> None:
    entidades = [
        _usuario(100, [RolUsuario.COMISIONISTA], activo=True),
        _usuario(101, [RolUsuario.ADMINISTRATOR], activo=False),
    ]
    uc, repo = _make_uc(listar=(entidades, 2))
    dto = await uc.listar_async(page=1, page_size=10, texto="x", activo=None)
    assert dto.total == 2
    assert dto.items[0].uid == 100
    assert dto.items[0].roles == [RolUsuario.COMISIONISTA.value]
    assert dto.items[1].activo is False
    repo.listar_paginado_async.assert_awaited_once_with(
        page=1, page_size=10, texto="x", activo=None
    )
