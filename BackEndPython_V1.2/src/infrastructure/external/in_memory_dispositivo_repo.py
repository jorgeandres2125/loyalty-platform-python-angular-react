from __future__ import annotations

import asyncio

from src.domain.entities.dispositivo_usuario import DispositivoUsuario


class InMemoryDispositivoRepo:
    """AP-0014: dispositivos por usuario en memoria de proceso.

    Implementa DispositivoRepository (PEP 544): un dict indexado por (uid, device_hash)
    protegido por asyncio.Lock. Ambito de proceso: no se comparte entre workers ni
    replicas y se pierde al reiniciar; en produccion, sustituir por el adaptador SQL
    (tablas SECURITY_DEVICE y SECURITY_USER_DEVICE) sin cambiar la firma del puerto.
    """

    def __init__(self) -> None:
        self._datos: dict[tuple[int, str], DispositivoUsuario] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def obtener(self, uid: int, device_hash: str) -> DispositivoUsuario | None:
        async with self._lock:
            return self._datos.get((uid, device_hash))

    async def guardar(self, dispositivo: DispositivoUsuario) -> None:
        async with self._lock:
            self._datos[(dispositivo.uid, dispositivo.device_hash)] = dispositivo

    async def listar_por_usuario(self, uid: int) -> list[DispositivoUsuario]:
        async with self._lock:
            return [
                dispositivo
                for (clave_uid, _clave_hash), dispositivo in self._datos.items()
                if clave_uid == uid
            ]
