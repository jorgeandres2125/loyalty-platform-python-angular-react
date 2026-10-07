from __future__ import annotations

from typing import Protocol

from src.domain.entities.desafio_oob import DesafioOob


class DesafioOobStore(Protocol):
    """AP-0005: almacen con expiracion (TTL) de los desafios OOB.

    Contrato estructural (PEP 544). El adaptador por defecto es en memoria; un Redis o
    SQL puede sustituirlo sin cambiar la firma. El TTL (vencimiento del desafio) lo
    aplica el adaptador: `obtener` devuelve None cuando el desafio ya expiro.
    """

    async def guardar(self, desafio_id: str, desafio: DesafioOob) -> None: ...
    async def obtener(self, desafio_id: str) -> DesafioOob | None: ...
    async def eliminar(self, desafio_id: str) -> None: ...
