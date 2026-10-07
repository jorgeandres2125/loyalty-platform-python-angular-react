from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from fastapi.routing import APIRoute

from src.adapters.api.main import app as app_real
from src.infrastructure.config.dependencies import require_token

_AUTHZ_MODULE = "src.infrastructure.config.permission_dependencies"

# Endpoints autenticados EXENTOS de permiso de rol: son de autoservicio (el actor
# solo opera sobre SI MISMO, la autenticacion es la autorizacion), de intercambio
# de token para el usuario ya logueado, o de depuracion (solo dev). El ownership
# implicito se resuelve por el "sub" del token en el caso de uso. Toda excepcion es
# explicita y justificada: eso es deny-by-default.
_AUTOSERVICIO: frozenset[str] = frozenset(
    {
        bytes.fromhex("2f6170692f76312f617574682f72656672657368").decode(),  # AP-0129 renovar sesion propia
        bytes.fromhex("2f6170692f76312f6d652f736573696f6e6573").decode(),  # AP-0130 mis sesiones (listar)
        bytes.fromhex("2f6170692f76312f6d652f736573696f6e65732f7b7369647d").decode(),  # AP-0130 cerrar sesion propia
        bytes.fromhex("2f6170692f76312f6d652f736573696f6e65732f6365727261722d6f74726173").decode(),  # AP-0130 cerrar otras
        "/api/v1/auth/me",
        "/api/v1/auth/password",
        "/api/v1/auth/logout-all",
        "/api/v1/oauth/token",
        "/api/v1/oidc/token",
        "/api/v1/debug/settings",
        # AP-0053 F6: firma digital es autoservicio puro (emisor=token.sub, sin
        # parametro de tercero); F3 lo etiqueto por error con FIRMA_GESTIONAR (solo
        # staff/webmaster), lo que bloqueaba a comisionista/comisionista_consumo de
        # firmar su propio contrato o autorizar su propia transaccion OOB.
        "/api/v1/firmas",
        "/api/v1/firmas/verificar",
    }
)


def _flatten(dependant: Any) -> Iterator[Any]:
    for dep in dependant.dependencies:
        yield dep
        yield from _flatten(dep)


def _requiere_autenticacion(route: APIRoute) -> bool:
    return any(dep.call is require_token for dep in _flatten(route.dependant))


def _tiene_autorizacion(route: APIRoute) -> bool:
    return any(
        getattr(dep.call, "__module__", "") == _AUTHZ_MODULE
        for dep in _flatten(route.dependant)
    )


def test_deny_by_default_todo_endpoint_autenticado_autoriza() -> None:
    faltantes: list[str] = sorted(
        route.path
        for route in app_real.routes
        if isinstance(route, APIRoute)
        and _requiere_autenticacion(route)
        and not _tiene_autorizacion(route)
        and route.path not in _AUTOSERVICIO
    )
    assert not faltantes, f"Endpoints autenticados sin autorizacion (AP-0053): {faltantes}"


def test_cobertura_rbac_no_vacia() -> None:
    cubiertos: list[str] = [
        route.path
        for route in app_real.routes
        if isinstance(route, APIRoute) and _tiene_autorizacion(route)
    ]
    assert len(cubiertos) >= 20
