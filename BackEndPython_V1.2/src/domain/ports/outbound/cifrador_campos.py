from __future__ import annotations

from typing import Protocol


class CifradorCampos(Protocol):
    """Puerto de salida para cifrado a nivel de aplicación de campos restringidos
    (AP-0147 / AP-0095). Contrato estructural (PEP 544): los adaptadores lo
    satisfacen por forma, sin heredar. El dominio nunca conoce el algoritmo.

    El AAD (Additional Authenticated Data) liga el criptograma a su ubicación
    lógica (tabla|columna|pk): un valor movido a otra fila/columna falla la
    verificación del tag y no descifra.
    """

    def cifrar(self, claro: str | None, *, aad: str) -> bytes | None: ...

    def descifrar(self, cifrado: bytes | None, *, aad: str) -> str | None: ...
