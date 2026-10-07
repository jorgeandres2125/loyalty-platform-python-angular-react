from __future__ import annotations

from src.domain.entities.bloqueo_duro import BloqueoDuro


class InMemoryBloqueoDuroRepo:
    """AP-0157: adaptador en memoria del bloqueo duro (ambito de proceso).

    Implementa BloqueoDuroRepository (PEP 544). Alternativa por defecto al adaptador SQL
    (tabla user_account_lock); se cambia por el durable en el composition root sin tocar
    el puerto.
    """

    def __init__(self) -> None:
        self._data: dict[int, BloqueoDuro] = {}

    async def obtener(self, uid: int) -> BloqueoDuro | None:
        return self._data.get(uid)

    async def guardar(self, estado: BloqueoDuro) -> None:
        self._data[estado.uid] = estado

    async def eliminar(self, uid: int) -> None:
        self._data.pop(uid, None)
