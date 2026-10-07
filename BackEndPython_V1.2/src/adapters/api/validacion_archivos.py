from __future__ import annotations

from pathlib import Path
from typing import Final

from fastapi import HTTPException, UploadFile, status

from src.shared.constants.content_types import CONTENT_TYPE_PDF

# AP-0138: firmas (magic bytes) por extension. Permite validar que la ESTRUCTURA
# del archivo corresponde con su extension declarada, no solo el nombre. Una
# extension sin firma conocida no se valida (no aplica).
_FIRMAS_POR_EXTENSION: Final[dict[str, tuple[bytes, ...]]] = {
    ".pdf": (b"%PDF-",),
    ".xlsx": (b"PK\x03\x04",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
}

# AP-0139: whitelist de tipos requeridos por el negocio. Los documentos del
# comisionista (cedula, RUT, contrato, certificados) son siempre PDF.
EXTENSIONES_DOCUMENTOS: Final[frozenset[str]] = frozenset({".pdf"})
MIME_DOCUMENTOS: Final[frozenset[str]] = frozenset({CONTENT_TYPE_PDF})


def _exceso(max_bytes: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
        detail=f"El archivo supera el tamano maximo permitido de {max_bytes} bytes.",
    )


def verificar_tamano_upload(file: UploadFile, max_bytes: int) -> None:
    """AP-0137: rechaza (413) un archivo cuyo tamano declarado supera el maximo.

    `UploadFile.size` lo fija el parser multipart de Starlette; cuando esta
    disponible permite rechazar antes de materializar el contenido en memoria.
    """
    tamano: int | None = file.size
    if tamano is not None and tamano > max_bytes:
        raise _exceso(max_bytes)


def verificar_tamano_contenido(contenido: bytes, max_bytes: int) -> None:
    """AP-0137: verificacion autoritativa por la longitud real ya leida.

    Cubre el caso en que `UploadFile.size` venga vacio: si el contenido excede el
    maximo configurado, se rechaza con 413.
    """
    if len(contenido) > max_bytes:
        raise _exceso(max_bytes)


def verificar_firma_archivo(contenido: bytes, nombre: str) -> None:
    """AP-0138: valida que el contenido empiece con la firma (magic bytes) que
    corresponde a la extension del archivo.

    Evita aceptar, por ejemplo, un ejecutable o un HTML renombrado a .pdf: aunque
    el sistema fuerce el nombre a .pdf, la estructura real debe coincidir. Una
    extension sin firma registrada no se valida. Rechaza con 415 si no coincide.
    """
    extension: str = Path(nombre).suffix.lower()
    firmas: tuple[bytes, ...] | None = _FIRMAS_POR_EXTENSION.get(extension)
    if firmas is None:
        return
    if not any(contenido.startswith(firma) for firma in firmas):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                "El contenido del archivo no corresponde a su extension "
                f"({extension}). Verifique que el archivo sea valido."
            ),
        )


def verificar_tipo_permitido(
    file: UploadFile,
    contenido: bytes,
    extensiones_permitidas: frozenset[str],
    mimes_permitidos: frozenset[str],
) -> None:
    """AP-0139: solo acepta archivos cuyo tipo y estructura estan en la whitelist
    requerida por el negocio.

    (1) El MIME declarado por el cliente debe estar en `mimes_permitidos`.
    (2) La estructura real (magic bytes) debe corresponder a uno de los formatos
        permitidos (`extensiones_permitidas`), de modo que un MIME falsificado no
        baste. Rechaza con 415 si no cumple. La capa (2) es la autoritativa.
    """
    mime_declarado: str = (file.content_type or "").split(";")[0].strip().lower()
    if mime_declarado and mime_declarado not in mimes_permitidos:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no permitido: {mime_declarado}.",
        )
    firmas_permitidas: tuple[bytes, ...] = tuple(
        firma
        for ext in extensiones_permitidas
        for firma in _FIRMAS_POR_EXTENSION.get(ext, ())
    )
    if firmas_permitidas and not any(
        contenido.startswith(firma) for firma in firmas_permitidas
    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="El archivo no es de un tipo permitido por el negocio.",
        )


def verificar_content_type_archivo(
    file: UploadFile, mimes_esperados: frozenset[str]
) -> None:
    """AP-0197: exige que el Content-Type declarado de la entrada sea el definido
    para el proceso.

    A diferencia de verificar_tipo_permitido (AP-0139, que tolera la ausencia de MIME
    y se apoya en los magic bytes), aqui el Content-Type es OBLIGATORIO: si falta o no
    esta en mimes_esperados se rechaza con 415.
    """
    mime: str = (file.content_type or "").split(";")[0].strip().lower()
    if not mime or mime not in mimes_esperados:
        permitidos: str = ", ".join(sorted(mimes_esperados))
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"El Content-Type de la entrada debe ser uno de: {permitidos}.",
        )
