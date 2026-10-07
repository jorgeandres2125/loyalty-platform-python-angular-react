"""Tests para ModuloPermisoEntity (catálogo plano: sin module_padre_id)."""
from __future__ import annotations

from dataclasses import fields

from src.domain.entities.modulo_permiso_entity import ModuloPermisoEntity


def _entidad_minima() -> ModuloPermisoEntity:
    return ModuloPermisoEntity(
        module_id=1,
        module_code="DASHBOARD",
        nombre="Dashboard",
        ruta="/dashboard",
        icono="bi-speedometer2",
        orden=10,
        puede_ver=True,
        puede_crear=False,
        puede_editar=False,
        puede_eliminar=False,
        puede_exportar=False,
        puede_aprobar=False,
    )


def test_entidad_construye_con_todos_los_campos() -> None:
    e = _entidad_minima()
    assert e.module_code == "DASHBOARD"
    assert e.puede_ver is True


def test_entidad_no_tiene_module_padre_id() -> None:
    """Decisión de diseño post-2026-05-19: el catálogo es plano."""
    nombres = {f.name for f in fields(ModuloPermisoEntity)}
    assert "module_padre_id" not in nombres


def test_entidad_tiene_exactamente_los_campos_esperados() -> None:
    esperados = {
        "module_id", "module_code", "nombre", "ruta", "icono", "orden",
        "puede_ver", "puede_crear", "puede_editar",
        "puede_eliminar", "puede_exportar", "puede_aprobar",
    }
    nombres = {f.name for f in fields(ModuloPermisoEntity)}
    assert nombres == esperados


def test_ruta_e_icono_aceptan_none() -> None:
    e = ModuloPermisoEntity(
        module_id=2,
        module_code="X",
        nombre="X",
        ruta=None,
        icono=None,
        orden=0,
        puede_ver=False,
        puede_crear=False,
        puede_editar=False,
        puede_eliminar=False,
        puede_exportar=False,
        puede_aprobar=False,
    )
    assert e.ruta is None
    assert e.icono is None
