from __future__ import annotations

from datetime import datetime
from typing import Protocol

from src.domain.entities.sesion_activa_entity import SesionActiva
from src.domain.value_objects.estado_sesion import EstadoSesion
from src.domain.value_objects.motivo_cierre_sesion import MotivoCierreSesion


class SesionRepository(Protocol):
    """AP-0130: puerto del Session Registry. Lo implementa un adaptador en memoria (un
    proceso) o, en produccion, Redis o SQL compartido (multi-instancia, AP-0081)."""

    async def crear(self, sesion: SesionActiva) -> None:
        ...

    async def obtener(self, sid: str) -> SesionActiva | None:
        ...

    async def listar_activas(self, uid: int) -> list[SesionActiva]:
        ...

    async def esta_revocada(self, sid: str) -> bool:
        ...

    async def cerrar(
        self,
        sid: str,
        estado: EstadoSesion,
        motivo: MotivoCierreSesion,
        momento: datetime,
    ) -> None:
        ...

    async def actualizar_actividad(self, sid: str, momento: datetime) -> None:
        ...
