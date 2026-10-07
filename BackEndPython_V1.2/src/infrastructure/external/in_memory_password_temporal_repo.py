from __future__ import annotations

from dataclasses import replace

from src.domain.entities.password_temporal_entity import PasswordTemporalEntity
from src.domain.value_objects.estado_password_temporal import EstadoPasswordTemporal


class InMemoryPasswordTemporalRepo:
    """Adaptador en memoria de PasswordTemporalRepository para pruebas.

    Mismo contrato que el adaptador SQL: crear invalida las vigentes previas y
    asigna id incremental; las marcas de uso y consumo transicionan el estado.
    """

    def __init__(self) -> None:
        self._filas: list[PasswordTemporalEntity] = []
        self._siguiente_id: int = 1

    async def obtener_vigente(self, uid: int) -> PasswordTemporalEntity | None:
        vigentes: list[PasswordTemporalEntity] = [
            fila
            for fila in self._filas
            if fila.uid == uid
            and fila.estado
            in (EstadoPasswordTemporal.ACTIVA, EstadoPasswordTemporal.USADA)
        ]
        if not vigentes:
            return None
        return max(vigentes, key=lambda fila: fila.emitida_iso)

    async def crear(self, entidad: PasswordTemporalEntity) -> PasswordTemporalEntity:
        self._filas = [
            replace(fila, estado=EstadoPasswordTemporal.REEMPLAZADA)
            if fila.uid == entidad.uid
            and fila.estado
            in (EstadoPasswordTemporal.ACTIVA, EstadoPasswordTemporal.USADA)
            else fila
            for fila in self._filas
        ]
        creada: PasswordTemporalEntity = replace(
            entidad,
            id=self._siguiente_id,
            estado=EstadoPasswordTemporal.ACTIVA,
            usada_iso=None,
            consumida_iso=None,
        )
        self._siguiente_id += 1
        self._filas.append(creada)
        return creada

    async def marcar_usada(self, temporal_id: int, usada_iso: str) -> None:
        self._filas = [
            replace(fila, usada_iso=usada_iso, estado=EstadoPasswordTemporal.USADA)
            if fila.id == temporal_id
            else fila
            for fila in self._filas
        ]

    async def marcar_consumida(self, temporal_id: int, consumida_iso: str) -> None:
        self._filas = [
            replace(
                fila,
                consumida_iso=consumida_iso,
                estado=EstadoPasswordTemporal.CONSUMIDA,
            )
            if fila.id == temporal_id
            else fila
            for fila in self._filas
        ]
