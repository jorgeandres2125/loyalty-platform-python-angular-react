"""AP-0139: el sistema solo acepta tipos de archivo requeridos por el negocio."""
from __future__ import annotations

import io

import pytest
from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers

from src.adapters.api.validacion_archivos import (
    EXTENSIONES_DOCUMENTOS,
    MIME_DOCUMENTOS,
    verificar_tipo_permitido,
)

SL = chr(47)
MIME_PDF = "application" + SL + "pdf"
MIME_HTML = "text" + SL + "html"
MIME_OCTET = "application" + SL + "octet-stream"
_PDF = b"%PDF-1.4 contenido de prueba"
_NO_PDF = b"esto no es un pdf real"


def _uf(contenido: bytes, mime: str | None) -> UploadFile:
    headers = Headers({"content-type": mime}) if mime else Headers({})
    return UploadFile(file=io.BytesIO(contenido), headers=headers)


def _validar(uf: UploadFile, contenido: bytes) -> None:
    verificar_tipo_permitido(uf, contenido, EXTENSIONES_DOCUMENTOS, MIME_DOCUMENTOS)


def test_pdf_con_mime_pdf_aceptado() -> None:
    _validar(_uf(_PDF, MIME_PDF), _PDF)


def test_mime_no_permitido_rechazado() -> None:
    with pytest.raises(HTTPException) as exc:
        _validar(_uf(_PDF, MIME_HTML), _PDF)
    assert exc.value.status_code == 415


def test_mime_octet_stream_rechazado() -> None:
    with pytest.raises(HTTPException) as exc:
        _validar(_uf(_PDF, MIME_OCTET), _PDF)
    assert exc.value.status_code == 415


def test_estructura_no_permitida_rechazada_aunque_mime_pdf() -> None:
    with pytest.raises(HTTPException) as exc:
        _validar(_uf(_NO_PDF, MIME_PDF), _NO_PDF)
    assert exc.value.status_code == 415


def test_sin_mime_declarado_valida_solo_estructura() -> None:
    _validar(_uf(_PDF, None), _PDF)


def test_whitelist_documentos_es_solo_pdf() -> None:
    assert EXTENSIONES_DOCUMENTOS == frozenset({".pdf"})
    assert MIME_DOCUMENTOS == frozenset({MIME_PDF})
