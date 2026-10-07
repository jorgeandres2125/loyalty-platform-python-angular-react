from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.bloqueo_duro import BloqueoDuro
from src.infrastructure.persistence.models.user_account_lock_model import (
    UserAccountLockModel,
)


class SQLAlchemyBloqueoDuroRepo:
    """AP-0157: adaptador SQL durable del bloqueo duro (tabla user_account_lock).

    Implementa BloqueoDuroRepository (PEP 544). Alternativa persistente y compartida entre
    replicas al adaptador en memoria; se cablea cambiando una linea en el composition root.
    Aplica la DDL de sql/user_account_lock.sql.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def obtener(self, uid: int) -> BloqueoDuro | None:
        model: UserAccountLockModel | None = await self._session.get(
            UserAccountLockModel, uid
        )
        return self._a_entidad(model) if model is not None else None

    async def guardar(self, estado: BloqueoDuro) -> None:
        model: UserAccountLockModel | None = await self._session.get(
            UserAccountLockModel, estado.uid
        )
        if model is None:
            model = UserAccountLockModel(uid=estado.uid)
            self._session.add(model)
        model.activo = estado.activo
        model.motivo = estado.motivo
        model.bloqueado_en_epoch = estado.bloqueado_en_epoch
        model.bloqueado_por_uid = estado.bloqueado_por_uid
        await self._session.commit()

    async def eliminar(self, uid: int) -> None:
        await self._session.execute(
            delete(UserAccountLockModel).where(UserAccountLockModel.uid == uid)
        )
        await self._session.commit()

    @staticmethod
    def _a_entidad(model: UserAccountLockModel) -> BloqueoDuro:
        return BloqueoDuro(
            uid=model.uid,
            activo=model.activo,
            motivo=model.motivo,
            bloqueado_en_epoch=model.bloqueado_en_epoch,
            bloqueado_por_uid=model.bloqueado_por_uid,
        )
