from __future__ import annotations

from typing import Protocol

from src.domain.entities.dispositivo_usuario import DispositivoUsuario


class DispositivoRepository(Protocol):
    """AP-0014: persistencia de los dispositivos por usuario (equipos origen).

    Contrato estructural (PEP 544). El adaptador por defecto es en memoria; en produccion
    un adaptador SQL (tablas SECURITY_DEVICE y SECURITY_USER_DEVICE) lo hace durable sin
    cambiar la firma del puerto.
    """

    async def obtener(self, uid: int, device_hash: str) -> DispositivoUsuario | None: ...
    async def guardar(self, dispositivo: DispositivoUsuario) -> None: ...
    async def listar_por_usuario(self, uid: int) -> list[DispositivoUsuario]: ...
