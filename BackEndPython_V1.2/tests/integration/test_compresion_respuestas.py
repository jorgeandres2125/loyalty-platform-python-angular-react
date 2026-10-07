"""AP-0035: compresión de todo lo transferido al cliente.

Verifica dos cosas:
1. Cableado: la app real registra CompressMiddleware (por dentro de CORS).
2. Comportamiento: negociación zstd→brotli→gzip por Accept-Encoding y respeto del
   umbral mínimo (cuerpos pequeños no se comprimen).

El comportamiento se prueba sobre una mini-app que monta el MISMO middleware con la
misma configuración por defecto, para no depender de endpoints autenticados/DB.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette_compress import CompressMiddleware

from src.adapters.api.main import app as app_real
from src.infrastructure.config.settings import Settings

_SETTINGS: Settings = Settings()
_CARGA_GRANDE: str = "SUFI-" * 400  # ~2000 bytes, muy por encima del umbral
_CARGA_PEQUENA: str = "ok"          # por debajo del umbral → no se comprime


def _mini_app() -> FastAPI:
    mini: FastAPI = FastAPI()
    mini.add_middleware(CompressMiddleware, minimum_size=_SETTINGS.compress_minimum_size)

    @mini.get("/grande")
    def grande() -> dict:
        return {"data": _CARGA_GRANDE}

    @mini.get("/pequeno")
    def pequeno() -> dict:
        return {"data": _CARGA_PEQUENA}

    return mini


_cliente: TestClient = TestClient(_mini_app())


# ── 1. Cableado en la app real ────────────────────────────────────────────────

def test_app_real_registra_compress_middleware() -> None:
    clases = [m.cls for m in app_real.user_middleware]
    assert CompressMiddleware in clases, "CompressMiddleware no está registrado en la app"


def test_compresion_va_por_dentro_de_cors() -> None:
    """CORS debe seguir siendo el más externo (primero en user_middleware)."""
    clases = [m.cls for m in app_real.user_middleware]
    assert clases.index(CORSMiddleware) < clases.index(CompressMiddleware)


# ── 2. Negociación por Accept-Encoding ────────────────────────────────────────

def test_brotli_cuando_el_cliente_lo_acepta() -> None:
    resp = _cliente.get("/grande", headers={"Accept-Encoding": "br"})
    assert resp.status_code == 200
    assert resp.headers.get("content-encoding") == "br"


def test_gzip_cuando_solo_se_acepta_gzip() -> None:
    resp = _cliente.get("/grande", headers={"Accept-Encoding": "gzip"})
    assert resp.status_code == 200
    assert resp.headers.get("content-encoding") == "gzip"
    # httpx descomprime de forma transparente → el JSON sigue siendo legible.
    assert resp.json()["data"] == _CARGA_GRANDE


# ── 3. Identidad y umbral mínimo ──────────────────────────────────────────────

def test_sin_accept_encoding_no_comprime() -> None:
    resp = _cliente.get("/grande", headers={"Accept-Encoding": "identity"})
    assert resp.status_code == 200
    assert resp.headers.get("content-encoding") in (None, "identity")


def test_cuerpo_por_debajo_del_umbral_no_se_comprime() -> None:
    resp = _cliente.get("/pequeno", headers={"Accept-Encoding": "br, gzip"})
    assert resp.status_code == 200
    assert resp.headers.get("content-encoding") is None
