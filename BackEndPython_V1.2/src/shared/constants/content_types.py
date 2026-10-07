"""AP-0103 -- Content-Type explicito para archivos generados dinamicamente.

Toda respuesta que entregue un archivo construido por el sistema (reportes XLSX,
documentos PDF servidos, etc.) debe declarar un Content-Type explicito. Estas
constantes son la unica fuente de verdad; `content_type_por_nombre` resuelve el
tipo por la extension real y NUNCA delega en la inferencia del navegador.
"""
from __future__ import annotations

from pathlib import Path
from typing import Final

CONTENT_TYPE_PDF: Final[str] = "application/pdf"
CONTENT_TYPE_XLSX: Final[str] = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
CONTENT_TYPE_OCTET_STREAM: Final[str] = "application/octet-stream"

CONTENT_TYPE_POR_EXTENSION: Final[dict[str, str]] = {
    ".pdf": CONTENT_TYPE_PDF,
    ".xlsx": CONTENT_TYPE_XLSX,
}


def content_type_por_nombre(nombre: str) -> str:
    """Content-Type explicito segun la extension del archivo (AP-0103).

    Devuelve application/octet-stream cuando la extension no se reconoce, de modo
    que el resultado SIEMPRE es un tipo explicito y nunca None ni una respuesta
    sujeta a sniffing del cliente.
    """
    extension: str = Path(nombre).suffix.lower()
    return CONTENT_TYPE_POR_EXTENSION.get(extension, CONTENT_TYPE_OCTET_STREAM)
