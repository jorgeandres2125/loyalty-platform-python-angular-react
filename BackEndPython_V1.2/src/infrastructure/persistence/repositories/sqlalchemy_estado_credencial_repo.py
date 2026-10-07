from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models.user_token_version_model import UserTokenVersionModel
from src.shared.constants.sesion import TOKEN_VERSION_INICIAL


class SQLAlchemyEstadoCredencialRepo:
    """AP-0021: adaptador SQL durable del token_version (tabla user_token_version).

    Implementa EstadoCredencialRepository (PEP 544). Alternativa persistente y compartida
    entre replicas al adaptador en memoria; se cablea cambiando una linea en el
    composition root. DDL en sql/ap0021_sesiones.sql.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def obtener_version(self, uid: int) -> int:
        model: UserTokenVersionModel | None = await self._session.get(
            UserTokenVersionModel, uid
        )
        return model.token_version if model is not None else TOKEN_VERSION_INICIAL

    async def incrementar_version(self, uid: int) -> int:
        model: UserTokenVersionModel | None = await self._session.get(
            UserTokenVersionModel, uid
        )
        if model is None:
            model = UserTokenVersionModel(uid=uid, token_version=TOKEN_VERSION_INICIAL + 1)
            self._session.add(model)
        else:
            model.token_version = model.token_version + 1
        model.updated_at = datetime.now(UTC).replace(tzinfo=None)
        await self._session.commit()
        return model.token_version
