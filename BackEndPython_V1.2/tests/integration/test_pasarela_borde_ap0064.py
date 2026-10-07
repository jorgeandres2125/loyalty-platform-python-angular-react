from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.middleware.pasarela_borde_middleware import PasarelaBordeMiddleware

_S: str = chr(47)
_SECRETO: str = "edge-secreto-de-prueba"
_HEADER: str = "X-Edge-Gateway"
_RECURSO: str = _S + "recurso"
_HEALTH: str = _S + "api" + _S + "v1" + _S + "health"


def _app(enabled: bool) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        PasarelaBordeMiddleware,
        edge_secret=_SECRETO,
        header=_HEADER,
        rutas_exentas=(_HEALTH,),
        enabled=enabled,
    )

    def recurso() -> dict[str, str]:
        return {"ok": "si"}

    def salud() -> dict[str, str]:
        return {"salud": "ok"}

    app.add_api_route(_RECURSO, recurso, methods=["GET"])
    app.add_api_route(_HEALTH + _S + "hora", salud, methods=["GET"])
    return app


def test_deshabilitado_deja_pasar_sin_cabecera() -> None:
    cliente = TestClient(_app(enabled=False))
    assert cliente.get(_RECURSO).status_code == 200


def test_habilitado_con_cabecera_valida_pasa() -> None:
    cliente = TestClient(_app(enabled=True))
    resp = cliente.get(_RECURSO, headers={_HEADER: _SECRETO})
    assert resp.status_code == 200


def test_habilitado_sin_cabecera_rechaza_403() -> None:
    cliente = TestClient(_app(enabled=True))
    assert cliente.get(_RECURSO).status_code == 403


def test_habilitado_cabecera_incorrecta_rechaza_403() -> None:
    cliente = TestClient(_app(enabled=True))
    resp = cliente.get(_RECURSO, headers={_HEADER: "valor-incorrecto"})
    assert resp.status_code == 403


def test_ruta_health_exenta_pasa_sin_cabecera() -> None:
    cliente = TestClient(_app(enabled=True))
    assert cliente.get(_HEALTH + _S + "hora").status_code == 200
