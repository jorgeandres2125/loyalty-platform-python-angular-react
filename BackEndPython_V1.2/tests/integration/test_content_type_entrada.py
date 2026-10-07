from __future__ import annotations

import io

import pytest
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.testclient import TestClient
from starlette.datastructures import Headers

from src.adapters.api.validacion_archivos import (
    MIME_DOCUMENTOS,
    verificar_content_type_archivo,
)

SL = chr(47)
MIME_PDF = "application" + SL + "pdf"
MIME_HTML = "text" + SL + "html"
_PDF = b"%PDF-1.4 prueba"


def _uf(mime):
    headers = Headers({"content-type": mime}) if mime else Headers({})
    return UploadFile(file=io.BytesIO(_PDF), headers=headers)


class TestContentTypeEntrada:
    """AP-0197: el Content-Type de la entrada debe ser el definido (PDF), obligatorio."""

    def test_pdf_declarado_aceptado(self) -> None:
        verificar_content_type_archivo(_uf(MIME_PDF), MIME_DOCUMENTOS)

    def test_pdf_con_charset_aceptado(self) -> None:
        verificar_content_type_archivo(_uf(MIME_PDF + "; charset=binary"), MIME_DOCUMENTOS)

    def test_sin_content_type_rechazado(self) -> None:
        with pytest.raises(HTTPException) as exc:
            verificar_content_type_archivo(_uf(None), MIME_DOCUMENTOS)
        assert exc.value.status_code == 415

    def test_content_type_incorrecto_rechazado(self) -> None:
        with pytest.raises(HTTPException) as exc:
            verificar_content_type_archivo(_uf(MIME_HTML), MIME_DOCUMENTOS)
        assert exc.value.status_code == 415


def _mini_app() -> FastAPI:
    app = FastAPI()

    @app.post(SL + "up")
    async def up(file: UploadFile = File(...)) -> dict:
        verificar_content_type_archivo(file, MIME_DOCUMENTOS)
        return {"ok": True}

    return app


_C = TestClient(_mini_app())


def test_endpoint_pdf_aceptado() -> None:
    r = _C.post(SL + "up", files={"file": ("doc.pdf", _PDF, MIME_PDF)})
    assert r.status_code == 200


def test_endpoint_content_type_incorrecto_415() -> None:
    r = _C.post(SL + "up", files={"file": ("doc.pdf", _PDF, MIME_HTML)})
    assert r.status_code == 415
