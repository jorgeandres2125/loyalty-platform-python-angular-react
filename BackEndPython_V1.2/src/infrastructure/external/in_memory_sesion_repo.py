from __future__ import annotations

import asyncio
from datetime import datetime

from src.domain.entities.sesion_activa_entity import SesionActiva
from src.domain.value_objects.estado_sesion import EstadoSesion
from src.domain.value_objects.motivo_cierre_sesion import MotivoCierreSesion


class InMemorySesionRepo:
    """AP-0130: Session Registry en memoria de proceso (adaptador por defecto). Satisface
    SesionRepository (PEP 544). NO comparte estado entre replicas; en produccion se
    sustituye por un adaptador Redis o SQL sin cambiar la firma del puerto (AP-0081)."""

    def __init__(self) -> None:
        self._por_sid: dict[str, SesionActiva] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def crear(self, sesion: SesionActiva) -> None:
        async with self._lock:
            self._por_sid[sesion.sid] = sesion

    async def obtener(self, sid: str) -> SesionActiva | None:
        async with self._lock:
            return self._por_sid.get(sid)

    async def listar_activas(self, uid: int) -> list[SesionActiva]:
        async with self._lock:
            return [
                s
                for s in self._por_sid.values()
                if s.uid == uid and s.estado == EstadoSesion.ACTIVA
            ]

    async def esta_revocada(self, sid: str) -> bool:
        async with self._lock:
            sesion: SesionActiva | None = self._por_sid.get(sid)
            return sesion is not None and sesion.estado != EstadoSesion.ACTIVA

    async def cerrar(
        self,
        sid: str,
        estado: EstadoSesion,
        motivo: MotivoCierreSesion,
        momento: datetime,
    ) -> None:
        # AP-0132: transiciona la sesion a un estado terminal y deja evidencia (motivo y
        # fecha de cierre). Idempotente: solo cierra sesiones aun activas, preservando el
        # primer motivo de cierre.
        async with self._lock:
            sesion: SesionActiva | None = self._por_sid.get(sid)
            if sesion is not None and sesion.estado == EstadoSesion.ACTIVA:
                sesion.estado = estado
                sesion.motivo_cierre = motivo
                sesion.fecha_cierre = momento

    async def actualizar_actividad(self, sid: str, momento: datetime) -> None:
        async with self._lock:
            sesion: SesionActiva | None = self._por_sid.get(sid)
            if sesion is not None:
                sesion.last_activity = momento
