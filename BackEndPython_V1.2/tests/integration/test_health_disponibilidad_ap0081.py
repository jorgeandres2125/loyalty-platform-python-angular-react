from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.routers import health_router
from src.infrastructure.config.dependencies import get_sonda_disponibilidad

_S: str = chr(47)
_BASE: str = _S + "api" + _S + "v1" + _S + "health"


class _SondaFalsa:
    """Doble de prueba del puerto SondaDisponibilidad (AP-0081)."""

    def __init__(self, disponible: bool) -> None:
        self._disponible: bool = disponible

    async def base_datos_disponible(self) -> bool:
        return self._disponible


def _app(bd_disponible: bool) -> FastAPI:
    app = FastAPI()
    app.include_router(health_router.router, prefix=_BASE)
    app.dependency_overrides[get_sonda_disponibilidad] = lambda: _SondaFalsa(bd_disponible)
    return app


def test_liveness_siempre_200() -> None:
    cliente = TestClient(_app(bd_disponible=False))
    resp = cliente.get(_BASE + _S + "live")
    assert resp.status_code == 200
    assert resp.json()["estado"] == "vivo"


def test_readiness_200_cuando_bd_disponible() -> None:
    cliente = TestClient(_app(bd_disponible=True))
    resp = cliente.get(_BASE + _S + "ready")
    assert resp.status_code == 200
    cuerpo = resp.json()
    assert cuerpo["estado"] == "listo"
    assert cuerpo["base_datos"] is True


def test_readiness_503_cuando_bd_no_disponible() -> None:
    cliente = TestClient(_app(bd_disponible=False))
    resp = cliente.get(_BASE + _S + "ready")
    assert resp.status_code == 503
    cuerpo = resp.json()
    assert cuerpo["estado"] == "no-listo"
    assert cuerpo["base_datos"] is False
