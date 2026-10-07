from __future__ import annotations

import asyncio

from src.domain.entities.evidencia_firma import EvidenciaFirma


class InMemoryEvidenciaFirmaStore:
    """AP-0006: almacen de evidencias de firma en memoria de proceso.

    Implementa EvidenciaFirmaStore (PEP 544): una lista ordenada por insercion
    protegida por asyncio.Lock y un indice por id. `ultimo` devuelve la evidencia mas
    reciente para encadenar la siguiente. Ambito de proceso: el estado no se comparte
    entre workers ni replicas y se pierde al reiniciar; al escalar, sustituir por un
    adaptador SQL sin cambiar la firma del puerto.
    """

    def __init__(self) -> None:
        self._orden: list[EvidenciaFirma] = []
        self._indice: dict[str, EvidenciaFirma] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def guardar(self, evidencia: EvidenciaFirma) -> None:
        async with self._lock:
            self._orden.append(evidencia)
            self._indice[evidencia.id] = evidencia

    async def obtener(self, evidencia_id: str) -> EvidenciaFirma | None:
        async with self._lock:
            return self._indice.get(evidencia_id)

    async def ultimo(self) -> EvidenciaFirma | None:
        async with self._lock:
            return self._orden[-1] if self._orden else None
