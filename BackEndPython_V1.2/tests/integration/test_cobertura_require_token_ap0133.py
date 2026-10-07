"""AP-0133: guard de cobertura. Garantiza que NINGUN endpoint no publico pueda registrarse
sin require_token, que es el punto donde se revalida el estado del usuario en cada peticion.
Cierra el riesgo de que un router protegido quede expuesto por un descuido de registro."""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from fastapi.routing import APIRoute

from src.adapters.api.main import app as app_real
from src.infrastructure.config.dependencies import require_token

# Prefijos de endpoints PUBLICOS (no exigen JWT). Todo lo demas DEBE pasar por
# require_token. La lista es explicita y justificada: eso es fail-secure por defecto.
_PREFIJOS_PUBLICOS: tuple[str, ...] = (
    "/api/v1/auth",              # login, logout y cambio de password sin sesion
    "/api/v1/verificacion-email",   # AP-0004 doble opt-in por correo
    "/api/v1/config",           # AP-0137 limite de subida (referencia publica)
    "/api/v1/health",           # AP-0144 salud
    "/api/v1/oauth",            # AP-0146 token endpoint (valida credenciales por si mismo)
    "/api/v1/oidc",             # AP-0010 discovery y token
    "/.well-known",                 # AP-0010 discovery estandar
    "/health",                      # salud raiz
    "/openapi.json",
    "/docs",
    "/redoc",
)


def _flatten(dependant: Any) -> Iterator[Any]:
    for dep in dependant.dependencies:
        yield dep
        yield from _flatten(dep)


def _requiere_token(route: APIRoute) -> bool:
    return any(dep.call is require_token for dep in _flatten(route.dependant))


def _es_publica(path: str) -> bool:
    return path.startswith(_PREFIJOS_PUBLICOS)


def test_todo_endpoint_no_publico_exige_require_token() -> None:
    faltantes: list[str] = sorted(
        route.path
        for route in app_real.routes
        if isinstance(route, APIRoute)
        and not _es_publica(route.path)
        and not _requiere_token(route)
    )
    assert not faltantes, (
        "AP-0133: endpoints no publicos SIN require_token (un usuario bloqueado o "
        "inhabilitado podria operar alli): " + repr(faltantes)
    )


def test_cobertura_require_token_no_trivial() -> None:
    protegidos: list[str] = [
        route.path
        for route in app_real.routes
        if isinstance(route, APIRoute) and _requiere_token(route)
    ]
    assert len(protegidos) >= 20
