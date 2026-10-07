from __future__ import annotations

from typing import Protocol

from src.domain.entities.evidencia_firma import EvidenciaFirma


class EvidenciaFirmaStore(Protocol):
    """AP-0006: almacen de evidencias de firma (encadenadas por hash).

    Contrato estructural (PEP 544). `ultimo` devuelve la evidencia mas reciente para
    encadenar la siguiente (tamper-evident). El adaptador por defecto es en memoria;
    un SQL o Redis puede sustituirlo sin cambiar la firma.
    """

    async def guardar(self, evidencia: EvidenciaFirma) -> None: ...
    async def obtener(self, evidencia_id: str) -> EvidenciaFirma | None: ...
    async def ultimo(self) -> EvidenciaFirma | None: ...
