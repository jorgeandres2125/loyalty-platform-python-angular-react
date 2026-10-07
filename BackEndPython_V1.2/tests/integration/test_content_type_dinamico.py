"""AP-0103: los archivos generados dinamicamente declaran Content-Type explicito.

1. Unidad de `content_type_por_nombre` (resuelve por extension; nunca None).
2. Comportamiento sobre una mini-app que monta SecurityHeadersMiddleware con dos
   endpoints que imitan las respuestas reales (PDF FileResponse y XLSX Response):
   el Content-Type es explicito y se acompana de X-Content-Type-Options: nosniff.
3. Cableado: la app real registra SecurityHeadersMiddleware y los routers usan las
   constantes compartidas.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, Response
from fastapi.testclient import TestClient

from src.adapters.api.main import app as app_real
from src.adapters.api.middleware.security_headers_middleware import SecurityHeadersMiddleware
from src.shared.constants.content_types import (
    CONTENT_TYPE_OCTET_STREAM,
    CONTENT_TYPE_PDF,
    CONTENT_TYPE_XLSX,
    content_type_por_nombre,
)

_PDF_BYTES: bytes = b"%PDF-1.4 contenido de prueba"
_XLSX_BYTES: bytes = b"PK\x03\x04 contenido xlsx de prueba"


# ── 1. Resolucion por extension ───────────────────────────────────────────────

def test_content_type_pdf() -> None:
    assert content_type_por_nombre("cedula123.pdf") == CONTENT_TYPE_PDF


def test_content_type_xlsx() -> None:
    assert content_type_por_nombre("reporte_2026.xlsx") == CONTENT_TYPE_XLSX


def test_content_type_extension_desconocida_es_octet_stream() -> None:
    assert content_type_por_nombre("archivo.dat") == CONTENT_TYPE_OCTET_STREAM
    assert content_type_por_nombre("sin_extension") == CONTENT_TYPE_OCTET_STREAM


def test_content_type_ignora_mayusculas() -> None:
    assert content_type_por_nombre("DOC.PDF") == CONTENT_TYPE_PDF
    assert content_type_por_nombre("R.XLSX") == CONTENT_TYPE_XLSX


def test_content_type_nunca_vacio() -> None:
    for nombre in ("a.pdf", "b.xlsx", "c.zip", "d"):
        assert content_type_por_nombre(nombre)


# ── 2. Comportamiento HTTP sobre mini-app ─────────────────────────────────────

def _mini_app(tmp_pdf: Path) -> FastAPI:
    mini: FastAPI = FastAPI()
    mini.add_middleware(SecurityHeadersMiddleware, hsts_enabled=False)

    @mini.get("/pdf")
    def servir_pdf() -> FileResponse:
        return FileResponse(
            path=tmp_pdf,
            media_type=content_type_por_nombre(tmp_pdf.name),
            filename=tmp_pdf.name,
        )

    @mini.get("/xlsx")
    def generar_xlsx() -> Response:
        return Response(content=_XLSX_BYTES, media_type=CONTENT_TYPE_XLSX)

    return mini


def test_respuesta_pdf_content_type_explicito(tmp_path: Path) -> None:
    archivo: Path = tmp_path / "cedula999.pdf"
    archivo.write_bytes(_PDF_BYTES)
    cliente: TestClient = TestClient(_mini_app(archivo))
    resp = cliente.get("/pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == CONTENT_TYPE_PDF
    assert resp.headers["x-content-type-options"] == "nosniff"


def test_respuesta_xlsx_content_type_explicito(tmp_path: Path) -> None:
    archivo: Path = tmp_path / "x.pdf"
    archivo.write_bytes(_PDF_BYTES)
    cliente: TestClient = TestClient(_mini_app(archivo))
    resp = cliente.get("/xlsx")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == CONTENT_TYPE_XLSX
    assert resp.headers["x-content-type-options"] == "nosniff"


# ── 3. Cableado en la app real ────────────────────────────────────────────────

def test_app_real_registra_security_headers_middleware() -> None:
    clases = [m.cls for m in app_real.user_middleware]
    assert SecurityHeadersMiddleware in clases


def test_routers_usan_constantes_compartidas() -> None:
    from src.adapters.api.routers import documentos_router, reportes_router

    assert reportes_router.CONTENT_TYPE_XLSX == CONTENT_TYPE_XLSX
    assert reportes_router.CONTENT_TYPE_XLSX in (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    assert documentos_router.content_type_por_nombre("c.pdf") == CONTENT_TYPE_PDF
