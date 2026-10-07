from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Final

from openpyxl import Workbook, load_workbook
from openpyxl.packaging.core import DocumentProperties
from pypdf import PdfReader, PdfWriter

logger: logging.Logger = logging.getLogger(__name__)

_EXT_PDF: Final[str] = ".pdf"
_EXT_XLSX: Final[str] = ".xlsx"


class SanitizadorMetadatosArchivo:
    """AP-0085: elimina metadatos de archivos (PDF, XLSX) antes de exponerlos.

    Los tipos no soportados se devuelven sin cambios. Si la limpieza falla
    (archivo corrupto o protegido), se registra una advertencia y se devuelve el
    contenido original para no interrumpir la operacion; el evento queda auditado.
    """

    def sanitizar(self, contenido: bytes, nombre: str) -> bytes:
        extension: str = Path(nombre).suffix.lower()
        if extension == _EXT_PDF:
            return self._sanitizar_pdf(contenido, nombre)
        if extension == _EXT_XLSX:
            return self._sanitizar_xlsx(contenido, nombre)
        return contenido

    def _sanitizar_pdf(self, contenido: bytes, nombre: str) -> bytes:
        try:
            reader: PdfReader = PdfReader(io.BytesIO(contenido))
            writer: PdfWriter = PdfWriter()
            writer.append(reader)
            writer.metadata = None
            writer.xmp_metadata = None
            salida: io.BytesIO = io.BytesIO()
            writer.write(salida)
            return salida.getvalue()
        except Exception:
            logger.warning("sanitizar_pdf_fallo", extra={"archivo": nombre}, exc_info=True)
            return contenido

    def _sanitizar_xlsx(self, contenido: bytes, nombre: str) -> bytes:
        try:
            libro: Workbook = load_workbook(io.BytesIO(contenido))
            props: DocumentProperties = DocumentProperties()
            props.creator = ""
            props.lastModifiedBy = ""
            props.title = None
            props.subject = None
            props.description = None
            props.keywords = None
            props.category = None
            libro.properties = props
            salida: io.BytesIO = io.BytesIO()
            libro.save(salida)
            return salida.getvalue()
        except Exception:
            logger.warning("sanitizar_xlsx_fallo", extra={"archivo": nombre}, exc_info=True)
            return contenido
