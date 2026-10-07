from __future__ import annotations

from typing import Protocol

from src.domain.value_objects.algoritmo_firma import AlgoritmoFirma


class FirmadorDigital(Protocol):
    """AP-0006: puerto de firma y verificacion con clave asimetrica.

    Contrato estructural (PEP 544). Abstrae la custodia de la clave privada: en
    desarrollo un adaptador con la libreria cryptography; en produccion un KMS o HSM
    que firma sin exponer la clave (operacion Sign remota). `firmar` recibe el mensaje
    canonico y devuelve la firma cruda; `verificar` valida esa firma sobre el mensaje.
    """

    kid: str
    algoritmo: AlgoritmoFirma

    def firmar(self, mensaje: bytes) -> bytes: ...
    def verificar(self, mensaje: bytes, firma: bytes) -> bool: ...
