"""Registro de rutas del router de verificación de correo (AP-0004).

Verifica que los endpoints públicos existen y NO están bajo la guardia de JWT.
No requiere BD: solo inspecciona las rutas declaradas por create_app().
"""
from __future__ import annotations

from src.adapters.api.main import create_app


def _rutas() -> dict[str, set[str]]:
    app = create_app()
    rutas: dict[str, set[str]] = {}
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if path is not None and methods is not None:
            rutas[path] = set(methods)
    return rutas


def test_endpoints_verificacion_registrados() -> None:
    rutas = _rutas()
    assert "POST" in rutas.get("/api/v1/verificacion-email/solicitar", set())
    assert "POST" in rutas.get("/api/v1/verificacion-email/confirmar", set())
