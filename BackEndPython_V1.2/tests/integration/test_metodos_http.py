from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.api.main import app as app_real
from src.adapters.api.middleware.metodos_http_middleware import MetodosHttpMiddleware

SL = chr(47)


def _mini_app() -> FastAPI:
    mini: FastAPI = FastAPI()
    mini.add_middleware(MetodosHttpMiddleware)

    @mini.get(SL + "r")
    def r() -> dict:
        return {"ok": True}

    return mini


_C: TestClient = TestClient(_mini_app())


class TestMetodosHttp:
    """AP-0185: solo se admiten los metodos HTTP minimos."""

    def test_get_permitido(self) -> None:
        assert _C.get(SL + "r").status_code == 200

    def test_trace_rechazado(self) -> None:
        resp = _C.request("TRACE", SL + "r")
        assert resp.status_code == 405
        assert "GET" in resp.headers.get("allow", "")

    def test_metodo_no_estandar_rechazado(self) -> None:
        assert _C.request("FOO", SL + "r").status_code == 405

    def test_post_permitido_por_middleware_405_del_router(self) -> None:
        # POST esta permitido por el middleware; el router responde 405 (no hay POST en la ruta)
        assert _C.post(SL + "r").status_code == 405


def test_app_real_registra_metodos_http_middleware() -> None:
    clases = [m.cls for m in app_real.user_middleware]
    assert MetodosHttpMiddleware in clases
