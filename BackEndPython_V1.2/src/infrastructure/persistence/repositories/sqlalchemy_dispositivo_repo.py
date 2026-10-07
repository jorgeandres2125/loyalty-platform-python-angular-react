from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.dispositivo_usuario import DispositivoUsuario
from src.infrastructure.persistence.models.security_user_device_model import (
    SecurityUserDeviceModel,
)


class SQLAlchemyDispositivoRepo:
    """AP-0014: adaptador SQL durable de dispositivos por usuario (SECURITY_USER_DEVICE).

    Implementa DispositivoRepository (PEP 544). Alternativa persistente y compartida entre
    replicas al adaptador en memoria; se cablea cambiando una linea en el composition root.
    DDL en sql/ap0014_dispositivos.sql.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def obtener(self, uid: int, device_hash: str) -> DispositivoUsuario | None:
        stmt = select(SecurityUserDeviceModel).where(
            SecurityUserDeviceModel.uid == uid,
            SecurityUserDeviceModel.device_hash == device_hash,
        )
        model: SecurityUserDeviceModel | None = (
            await self._session.execute(stmt)
        ).scalars().first()
        return self._a_entidad(model) if model is not None else None

    async def guardar(self, dispositivo: DispositivoUsuario) -> None:
        stmt = select(SecurityUserDeviceModel).where(
            SecurityUserDeviceModel.uid == dispositivo.uid,
            SecurityUserDeviceModel.device_hash == dispositivo.device_hash,
        )
        model: SecurityUserDeviceModel | None = (
            await self._session.execute(stmt)
        ).scalars().first()
        if model is None:
            model = SecurityUserDeviceModel(
                uid=dispositivo.uid, device_hash=dispositivo.device_hash
            )
            self._session.add(model)
        model.device_name = dispositivo.device_name
        model.user_agent = dispositivo.user_agent
        model.first_login_iso = dispositivo.first_login_iso
        model.last_login_iso = dispositivo.last_login_iso
        model.veces_visto = dispositivo.veces_visto
        model.trusted = dispositivo.trusted
        await self._session.commit()

    async def listar_por_usuario(self, uid: int) -> list[DispositivoUsuario]:
        stmt = select(SecurityUserDeviceModel).where(SecurityUserDeviceModel.uid == uid)
        modelos = (await self._session.execute(stmt)).scalars().all()
        return [self._a_entidad(model) for model in modelos]

    @staticmethod
    def _a_entidad(model: SecurityUserDeviceModel) -> DispositivoUsuario:
        return DispositivoUsuario(
            uid=model.uid,
            device_hash=model.device_hash,
            device_name=model.device_name,
            user_agent=model.user_agent,
            first_login_iso=model.first_login_iso,
            last_login_iso=model.last_login_iso,
            veces_visto=model.veces_visto,
            trusted=model.trusted,
        )
