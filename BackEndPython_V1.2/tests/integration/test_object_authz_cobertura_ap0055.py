from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from fastapi.routing import APIRoute

from src.adapters.api.main import app as app_real

_OBJ_MODULE = "src.adapters.api.object_authz"
# Routers cuyas rutas con id de recurso ({...}) exponen objetos sensibles y deben
# declarar autorizacion a nivel de objeto (require_object_access). Los catalogos de
# referencia (/admin/*) quedan fuera: son datos no sensibles restringidos por rol.
_PREFIJOS_OBJETO = (
    "/api/v1/documentos",
    "/api/v1/oob",
)


def _flatten(dependant: Any) -> Iterator[Any]:
    for dep in dependant.dependencies:
        yield dep
        yield from _flatten(dep)


def _tiene_object_authz(route: APIRoute) -> bool:
    return any(
        getattr(dep.call, "__module__", "") == _OBJ_MODULE
        for dep in _flatten(route.dependant)
    )


def test_toda_ruta_con_id_de_objeto_declara_object_authz() -> None:
    faltantes: list[str] = sorted(
        route.path
        for route in app_real.routes
        if isinstance(route, APIRoute)
        and route.path.startswith(_PREFIJOS_OBJETO)
        and "{" in route.path
        and not _tiene_object_authz(route)
    )
    assert not faltantes, (
        f"Rutas de objeto con id sin autorizacion por-objeto (AP-0055): {faltantes}"
    )


def test_cobertura_object_authz_no_vacia() -> None:
    cubiertas: list[str] = [
        route.path
        for route in app_real.routes
        if isinstance(route, APIRoute) and _tiene_object_authz(route)
    ]
    assert len(cubiertas) >= 5
