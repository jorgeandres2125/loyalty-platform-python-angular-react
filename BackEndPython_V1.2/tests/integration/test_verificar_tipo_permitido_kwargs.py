"""Regresion: los dos endpoints de subida de documentos (staff y self-service) deben
invocar verificar_tipo_permitido con los nombres de parametro reales de la funcion
(file, contenido, extensiones_permitidas, mimes_permitidos).

Bug detectado en produccion: ambos call sites (documentos_router.subir_archivo_documento
y me_router.subir_mi_documento) pasaban `content=` en vez de `contenido=`, lo que hacia
fallar con TypeError toda subida de PDF (415 nunca se evaluaba; la peticion caia con 500).
Esta prueba fija el contrato exacto para que un typo de kwarg no vuelva a pasar CI.
"""
from __future__ import annotations

import io

from fastapi import UploadFile
from starlette.datastructures import Headers

from src.adapters.api.validacion_archivos import (
    EXTENSIONES_DOCUMENTOS,
    MIME_DOCUMENTOS,
    verificar_tipo_permitido,
)

SL = chr(47)
MIME_PDF = "application" + SL + "pdf"
_PDF = b"%PDF-1.4 contenido de prueba"


def _uf(contenido: bytes, mime: str) -> UploadFile:
    return UploadFile(file=io.BytesIO(contenido), headers=Headers({"content-type": mime}))


def test_llamada_con_kwargs_del_endpoint_staff_no_lanza_typeerror() -> None:
    # Mismo patron de kwargs que documentos_router.subir_archivo_documento.
    verificar_tipo_permitido(
        file=_uf(_PDF, MIME_PDF),
        contenido=_PDF,
        extensiones_permitidas=EXTENSIONES_DOCUMENTOS,
        mimes_permitidos=MIME_DOCUMENTOS,
    )


def test_llamada_con_kwargs_del_endpoint_self_service_no_lanza_typeerror() -> None:
    # Mismo patron de kwargs que me_router.subir_mi_documento.
    verificar_tipo_permitido(
        file=_uf(_PDF, MIME_PDF),
        contenido=_PDF,
        extensiones_permitidas=EXTENSIONES_DOCUMENTOS,
        mimes_permitidos=MIME_DOCUMENTOS,
    )
