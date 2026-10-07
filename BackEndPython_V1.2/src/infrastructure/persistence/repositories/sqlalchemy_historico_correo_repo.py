from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.historico_correo_entity import HistoricoCorreoEntity
from src.infrastructure.persistence.models.historico_correo_model import HistoricoCorreoModel


class SQLAlchemyHistoricoCorreoRepo:
    """Adaptador de persistencia para `historico_correo` (implementa
    HistoricoCorreoRepository por forma)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def registrar_async(self, entity: HistoricoCorreoEntity) -> None:
        row: HistoricoCorreoModel = HistoricoCorreoModel(
            tipo_correo=entity.tipo_correo,
            usuario_envio=entity.usuario_envio,
            usuario_destino=entity.usuario_destino,
            fecha=entity.fecha,
            enviado=entity.enviado,
        )
        self._session.add(row)
        await self._session.flush()
