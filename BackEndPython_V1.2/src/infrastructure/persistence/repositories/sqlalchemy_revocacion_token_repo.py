from __future__ import annotations

import time

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models.revoked_token_model import RevokedTokenModel


class SQLAlchemyRevocacionTokenRepo:
    """AP-0021: adaptador SQL durable de la denylist de jti (tabla revoked_token).

    Implementa RevocacionTokenStore (PEP 544). Alternativa persistente al adaptador en
    memoria; se cablea cambiando una linea en el composition root. DDL en
    sql/ap0021_sesiones.sql.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def revocar(self, jti: str, ttl_segundos: int) -> None:
        model: RevokedTokenModel | None = await self._session.get(RevokedTokenModel, jti)
        if model is None:
            model = RevokedTokenModel(jti=jti)
            self._session.add(model)
        model.expira_en_epoch = time.time() + max(0, ttl_segundos)
        await self._session.commit()

    async def esta_revocado(self, jti: str) -> bool:
        model: RevokedTokenModel | None = await self._session.get(RevokedTokenModel, jti)
        if model is None:
            return False
        return time.time() < model.expira_en_epoch
