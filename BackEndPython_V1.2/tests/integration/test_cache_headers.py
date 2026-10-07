from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.testclient import TestClient

from src.adapters.api.main import app as app_real
from src.adapters.api.middleware.security_headers_middleware import SecurityHeadersMiddleware

SL = chr(47)


def _mini_app() -> FastAPI:
    mini: FastAPI = FastAPI()
    mini.add_middleware(SecurityHeadersMiddleware, hsts_enabled=False)

    @mini.get(SL + "datos")
    def datos() -> dict:
        return {"ok": True}

    @mini.get(SL + "docs")
    def docs() -> Response:
        return Response(content="swagger", media_type=("text" + SL + "html"))

    @mini.get(SL + "propia")
    def propia() -> Response:
        r: Response = Response(content="x")
        r.headers["Cache-Control"] = "public, max-age=60"
        return r

    return mini


_CLIENTE: TestClient = TestClient(_mini_app())


class TestCacheHeaders:
    """AP-0182: cabeceras de cache para respuestas no publicas."""

    def test_respuesta_sensible_no_store(self) -> None:
        resp = _CLIENTE.get(SL + "datos")
        assert "no-store" in resp.headers["cache-control"]
        assert resp.headers["pragma"] == "no-cache"
        assert resp.headers["expires"] == "0"

    def test_docs_es_cacheable(self) -> None:
        resp = _CLIENTE.get(SL + "docs")
        assert "no-store" not in resp.headers.get("cache-control", "")

    def test_respeta_cache_control_del_endpoint(self) -> None:
        resp = _CLIENTE.get(SL + "propia")
        assert resp.headers["cache-control"] == "public, max-age=60"


def test_app_real_registra_security_headers_middleware() -> None:
    clases = [m.cls for m in app_real.user_middleware]
    assert SecurityHeadersMiddleware in clases
