"""AP-0138: el sistema valida que la estructura del archivo coincida con su extension."""
from __future__ import annotations

import pytest
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.testclient import TestClient

from src.adapters.api.validacion_archivos import verificar_firma_archivo

SL = chr(47)
_PDF = b"%PDF-1.4 contenido de prueba"
_NO_PDF = b"esto no es un pdf real"
_XLSX = b"PK\x03\x04 resto del zip"


def test_pdf_valido_pasa() -> None:
    verificar_firma_archivo(_PDF, "cedula123.pdf")


def test_contenido_no_pdf_con_extension_pdf_rechazado() -> None:
    with pytest.raises(HTTPException) as exc:
        verificar_firma_archivo(_NO_PDF, "cedula123.pdf")
    assert exc.value.status_code == 415


def test_xlsx_valido_pasa() -> None:
    verificar_firma_archivo(_XLSX, "reporte.xlsx")


def test_xlsx_invalido_rechazado() -> None:
    with pytest.raises(HTTPException) as exc:
        verificar_firma_archivo(b"no soy xlsx", "reporte.xlsx")
    assert exc.value.status_code == 415


def test_extension_sin_firma_no_se_valida() -> None:
    verificar_firma_archivo(_NO_PDF, "archivo.dat")
    verificar_firma_archivo(_NO_PDF, "sin_extension")


def _make_client() -> TestClient:
    app = FastAPI()

    @app.post(SL + "up")
    async def up(file: UploadFile = File(...)) -> dict:
        contenido = await file.read()
        verificar_firma_archivo(contenido, "doc.pdf")
        return {"ok": True}

    return TestClient(app)


_CLIENT = _make_client()


def test_endpoint_acepta_pdf_real() -> None:
    r = _CLIENT.post(SL + "up", files={"file": ("doc.pdf", _PDF)})
    assert r.status_code == 200


def test_endpoint_rechaza_no_pdf_con_415() -> None:
    r = _CLIENT.post(SL + "up", files={"file": ("doc.pdf", _NO_PDF)})
    assert r.status_code == 415
