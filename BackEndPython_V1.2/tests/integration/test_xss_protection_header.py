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

    @mini.get(SL + "propia")
    def propia() -> Response:
        r: Response = Response(content="x")
        r.headers["X-XSS-Protection"] = "0"
        return r

    return mini


_CLIENTE: TestClient = TestClient(_mini_app())


class TestXssProtectionHeader:
    """AP-0202: cabecera X-XSS-Protection 1; mode=block (control heredado)."""

    def test_emite_xss_protection_por_defecto(self) -> None:
        resp = _CLIENTE.get(SL + "datos")
        assert resp.headers["x-xss-protection"] == "1; mode=block"

    def test_respeta_valor_propio_del_endpoint(self) -> None:
        resp = _CLIENTE.get(SL + "propia")
        assert resp.headers["x-xss-protection"] == "0"


def test_app_real_registra_security_headers_middleware() -> None:
    clases = [m.cls for m in app_real.user_middleware]
    assert SecurityHeadersMiddleware in clases
