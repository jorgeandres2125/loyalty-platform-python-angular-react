from __future__ import annotations

import asyncio

from src.shared.constants.sesion import TOKEN_VERSION_INICIAL


class InMemoryEstadoCredencialRepo:
    """AP-0021: token_version por usuario en memoria de proceso.

    Implementa EstadoCredencialRepository (PEP 544). Todo usuario nace en la version
    inicial; incrementarla invalida sus tokens vivos. Ambito de proceso: no se comparte
    entre workers ni replicas y se pierde al reiniciar (tras un reinicio todas las
    versiones vuelven a la inicial, que coincide con los tokens recien emitidos). En
    produccion, sustituir por el adaptador SQL (tabla user_token_version).
    """

    def __init__(self) -> None:
        self._versiones: dict[int, int] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def obtener_version(self, uid: int) -> int:
        async with self._lock:
            return self._versiones.get(uid, TOKEN_VERSION_INICIAL)

    async def incrementar_version(self, uid: int) -> int:
        async with self._lock:
            nueva: int = self._versiones.get(uid, TOKEN_VERSION_INICIAL) + 1
            self._versiones[uid] = nueva
            return nueva
