from __future__ import annotations

from typing import Protocol


class SanitizadorMetadatos(Protocol):
    """Puerto de salida (AP-0085): elimina metadatos de un archivo antes de
    compartirlo o exponerlo a un tercero. La implementacion despacha por tipo."""

    def sanitizar(self, contenido: bytes, nombre: str) -> bytes:
        """Devuelve los bytes del archivo sin metadatos identificables.

        nombre solo se usa para inferir el tipo por su extension; nunca se
        escribe dentro del archivo de salida.
        """
        ...
