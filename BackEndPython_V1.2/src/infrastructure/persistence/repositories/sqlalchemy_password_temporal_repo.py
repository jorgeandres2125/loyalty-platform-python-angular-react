from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.password_temporal_entity import PasswordTemporalEntity
from src.domain.value_objects.estado_password_temporal import EstadoPasswordTemporal
from src.domain.value_objects.origen_password_temporal import OrigenPasswordTemporal
from src.infrastructure.persistence.models.user_password_temporal_model import (
    UserPasswordTemporalModel,
)

_ESTADOS_VIGENTES: tuple[str, str] = (
    EstadoPasswordTemporal.ACTIVA.value,
    EstadoPasswordTemporal.USADA.value,
)


class SqlAlchemyPasswordTemporalRepo:
    """AP-0046, AP-0047 y AP-0048: adaptador SQL de credenciales temporales.

    Implementa PasswordTemporalRepository (PEP 544), ligado a la sesion de la
    peticion (el commit lo hace el ciclo de vida de la sesion). crear invalida las
    vigentes previas en la misma transaccion (nunca hay dos vigentes). DDL de
    referencia en sql (ap0046_password_temporal.sql) y migracion 20260703_0012.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def obtener_vigente(self, uid: int) -> PasswordTemporalEntity | None:
        stmt = (
            select(UserPasswordTemporalModel)
            .where(
                UserPasswordTemporalModel.uid == uid,
                UserPasswordTemporalModel.estado.in_(_ESTADOS_VIGENTES),
            )
            .order_by(UserPasswordTemporalModel.emitida_iso.desc())
            .limit(1)
        )
        fila: UserPasswordTemporalModel | None = (
            (await self._session.execute(stmt)).scalars().first()
        )
        return self._a_entidad(fila) if fila is not None else None

    async def crear(self, entidad: PasswordTemporalEntity) -> PasswordTemporalEntity:
        marcar = (
            update(UserPasswordTemporalModel)
            .where(
                UserPasswordTemporalModel.uid == entidad.uid,
                UserPasswordTemporalModel.estado.in_(_ESTADOS_VIGENTES),
            )
            .values(estado=EstadoPasswordTemporal.REEMPLAZADA.value)
        )
        await self._session.execute(marcar)
        fila: UserPasswordTemporalModel = UserPasswordTemporalModel(
            uid=entidad.uid,
            hash_temporal=entidad.hash_temporal,
            emitida_por_uid=entidad.emitida_por_uid,
            emitida_por_usuario=entidad.emitida_por_usuario,
            origen=entidad.origen.value,
            motivo=entidad.motivo,
            ip_emision=entidad.ip_emision,
            emitida_iso=entidad.emitida_iso,
            expira_iso=entidad.expira_iso,
            usada_iso=None,
            consumida_iso=None,
            estado=EstadoPasswordTemporal.ACTIVA.value,
        )
        self._session.add(fila)
        await self._session.flush()
        return self._a_entidad(fila)

    async def marcar_usada(self, temporal_id: int, usada_iso: str) -> None:
        stmt = (
            update(UserPasswordTemporalModel)
            .where(UserPasswordTemporalModel.id == temporal_id)
            .values(usada_iso=usada_iso, estado=EstadoPasswordTemporal.USADA.value)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def marcar_consumida(self, temporal_id: int, consumida_iso: str) -> None:
        stmt = (
            update(UserPasswordTemporalModel)
            .where(UserPasswordTemporalModel.id == temporal_id)
            .values(
                consumida_iso=consumida_iso,
                estado=EstadoPasswordTemporal.CONSUMIDA.value,
            )
        )
        await self._session.execute(stmt)
        await self._session.flush()

    @staticmethod
    def _a_entidad(fila: UserPasswordTemporalModel) -> PasswordTemporalEntity:
        return PasswordTemporalEntity(
            id=fila.id,
            uid=fila.uid,
            hash_temporal=fila.hash_temporal,
            emitida_por_uid=fila.emitida_por_uid,
            emitida_por_usuario=fila.emitida_por_usuario,
            origen=OrigenPasswordTemporal(fila.origen),
            motivo=fila.motivo,
            ip_emision=fila.ip_emision,
            emitida_iso=fila.emitida_iso,
            expira_iso=fila.expira_iso,
            usada_iso=fila.usada_iso,
            consumida_iso=fila.consumida_iso,
            estado=EstadoPasswordTemporal(fila.estado),
        )
