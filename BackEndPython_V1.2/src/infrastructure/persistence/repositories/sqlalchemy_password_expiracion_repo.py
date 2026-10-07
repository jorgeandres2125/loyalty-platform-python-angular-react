from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models.user_password_expiracion_model import (
    UserPasswordExpiracionModel,
)


class SqlAlchemyPasswordExpiracionRepo:
    """AP-0037: adaptador SQL del reloj de vencimiento (tabla user_password_expiracion).

    Implementa PasswordExpiracionRepository (PEP 544), ligado a la sesion de la
    peticion (el commit lo hace el ciclo de vida de la sesion). DDL de referencia
    en sql (ap0037_password_expiracion.sql) y migracion Alembic 20260703_0010.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def obtener_cambiado_en(self, uid: int) -> datetime | None:
        model: UserPasswordExpiracionModel | None = await self._session.get(
            UserPasswordExpiracionModel, uid
        )
        return model.password_cambiado_en if model is not None else None

    async def registrar_cambio(self, uid: int, cuando: datetime) -> None:
        model: UserPasswordExpiracionModel | None = await self._session.get(
            UserPasswordExpiracionModel, uid
        )
        if model is None:
            model = UserPasswordExpiracionModel(uid=uid, password_cambiado_en=cuando)
            self._session.add(model)
        else:
            model.password_cambiado_en = cuando
        model.updated_at = datetime.now(UTC).replace(tzinfo=None)
        await self._session.flush()

    async def asegurar_baseline(self, uid: int, cuando: datetime) -> None:
        # Arranca el contador solo si el usuario no tiene registro; nunca pisa uno
        # existente (idempotente en cada login posterior).
        model: UserPasswordExpiracionModel | None = await self._session.get(
            UserPasswordExpiracionModel, uid
        )
        if model is not None:
            return
        nuevo: UserPasswordExpiracionModel = UserPasswordExpiracionModel(
            uid=uid, password_cambiado_en=cuando
        )
        nuevo.updated_at = datetime.now(UTC).replace(tzinfo=None)
        self._session.add(nuevo)
        await self._session.flush()
