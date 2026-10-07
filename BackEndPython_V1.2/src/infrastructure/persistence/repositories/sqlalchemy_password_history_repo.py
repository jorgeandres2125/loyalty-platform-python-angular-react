from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models.user_password_history_model import (
    UserPasswordHistoryModel,
)


class SqlAlchemyPasswordHistoryRepo:
    """AP-0041: adaptador SQL del historial de contrasenas (user_password_history).

    Implementa PasswordHistoryRepository (PEP 544), ligado a la sesion de la peticion
    (el commit lo hace el ciclo de vida de la sesion, atomico con el cambio de clave).
    DDL de referencia en sql (ap0041_password_history.sql) y migracion 20260703_0011.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def ultimos_hashes(self, uid: int, cantidad: int) -> list[str]:
        stmt = (
            select(UserPasswordHistoryModel.password_hash)
            .where(UserPasswordHistoryModel.uid == uid)
            .order_by(UserPasswordHistoryModel.creado_iso.desc())
            .limit(cantidad)
        )
        filas = (await self._session.execute(stmt)).scalars().all()
        return list(filas)

    async def insertar(self, uid: int, password_hash: str, creado_iso: str) -> None:
        self._session.add(
            UserPasswordHistoryModel(
                uid=uid, password_hash=password_hash, creado_iso=creado_iso
            )
        )
        await self._session.flush()

    async def podar(self, uid: int, conservar: int) -> None:
        conservar_stmt = (
            select(UserPasswordHistoryModel.id)
            .where(UserPasswordHistoryModel.uid == uid)
            .order_by(UserPasswordHistoryModel.creado_iso.desc())
            .limit(conservar)
        )
        ids_conservar = (await self._session.execute(conservar_stmt)).scalars().all()
        if not ids_conservar:
            return
        del_stmt = delete(UserPasswordHistoryModel).where(
            UserPasswordHistoryModel.uid == uid,
            UserPasswordHistoryModel.id.notin_(ids_conservar),
        )
        await self._session.execute(del_stmt)
        await self._session.flush()
