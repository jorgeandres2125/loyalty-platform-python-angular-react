from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.bloqueo_cuenta import BloqueoCuenta
from src.infrastructure.persistence.models.user_lockout_model import UserLockoutModel


class SQLAlchemyBloqueoCuentaRepo:
    """AP-0009: adaptador SQL durable del estado de bloqueo (tabla user_lockout).

    Implementa BloqueoCuentaRepository (PEP 544). Alternativa persistente y compartida
    entre replicas al adaptador en memoria; se cablea cambiando una linea en el
    composition root (get_bloqueo_cuenta_repo). Aplica la DDL de sql/user_lockout.sql.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def obtener(self, clave: str) -> BloqueoCuenta | None:
        model: UserLockoutModel | None = await self._session.get(UserLockoutModel, clave)
        return self._a_entidad(model) if model is not None else None

    async def guardar(self, estado: BloqueoCuenta) -> None:
        model: UserLockoutModel | None = await self._session.get(
            UserLockoutModel, estado.clave
        )
        if model is None:
            model = UserLockoutModel(clave=estado.clave)
            self._session.add(model)
        model.conteo_fallos = estado.conteo_fallos
        model.bloqueada = estado.bloqueada
        model.bloqueada_en_epoch = estado.bloqueada_en_epoch
        model.expira_en_epoch = estado.expira_en_epoch
        model.motivo = estado.motivo
        await self._session.commit()

    async def eliminar(self, clave: str) -> None:
        await self._session.execute(
            delete(UserLockoutModel).where(UserLockoutModel.clave == clave)
        )
        await self._session.commit()

    @staticmethod
    def _a_entidad(model: UserLockoutModel) -> BloqueoCuenta:
        return BloqueoCuenta(
            clave=model.clave,
            conteo_fallos=model.conteo_fallos,
            bloqueada=model.bloqueada,
            bloqueada_en_epoch=model.bloqueada_en_epoch,
            expira_en_epoch=model.expira_en_epoch,
            motivo=model.motivo,
        )
