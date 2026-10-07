"""AP-0199: parametros de query repetidos se descartan (HTTP Parameter Pollution)."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from src.adapters.api.middleware.parametros_duplicados_middleware import (
    ParametrosDuplicadosMiddleware,
)
from src.shared.utils.parametros_duplicados import colapsar_parametros_duplicados

SL = chr(47)
_VACIO: frozenset[str] = frozenset()


def test_sin_duplicados_devuelve_identico() -> None:
    original = b"a=1&b=2&c=3"
    salida, dup = colapsar_parametros_duplicados(original, _VACIO)
    assert salida == original
    assert dup == []


def test_colapsa_conservando_la_primera() -> None:
    salida, dup = colapsar_parametros_duplicados(b"rol=user&rol=admin", _VACIO)
    assert salida == b"rol=user"
    assert dup == ["rol"]


def test_varios_nombres_duplicados_en_orden() -> None:
    salida, dup = colapsar_parametros_duplicados(b"a=1&b=2&a=9&b=8&a=7", _VACIO)
    assert salida == b"a=1&b=2"
    assert dup == ["a", "b"]


def test_nombre_multivalor_no_se_colapsa() -> None:
    salida, dup = colapsar_parametros_duplicados(
        b"tag=x&tag=y&rol=a&rol=b", frozenset({"tag"})
    )
    assert salida == b"tag=x&tag=y&rol=a"
    assert dup == ["rol"]


def test_query_vacio() -> None:
    salida, dup = colapsar_parametros_duplicados(b"", _VACIO)
    assert salida == b""
    assert dup == []


def test_conserva_valores_en_blanco_y_otros_intactos() -> None:
    salida, dup = colapsar_parametros_duplicados(b"q=&q=&page=2", _VACIO)
    assert salida == b"q=&page=2"
    assert dup == ["q"]


def _make_client() -> TestClient:
    app = FastAPI()
    app.add_middleware(ParametrosDuplicadosMiddleware)

    @app.get(SL + "eco")
    async def eco(request: Request) -> dict:
        return {
            "rol": request.query_params.get("rol"),
            "n": len(request.query_params.getlist("rol")),
        }

    return TestClient(app)


_CLIENT = _make_client()


def test_endpoint_descarta_parametro_repetido() -> None:
    r = _CLIENT.get(SL + "eco?rol=user&rol=admin")
    assert r.status_code == 200
    assert r.json() == {"rol": "user", "n": 1}


def test_endpoint_sin_repeticion_funciona_normal() -> None:
    r = _CLIENT.get(SL + "eco?rol=user")
    assert r.status_code == 200
    assert r.json() == {"rol": "user", "n": 1}
