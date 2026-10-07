from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.entities.registro_auditoria import RegistroAuditoria
from src.infrastructure.persistence.models.audit_log_model import AuditLogModel


class SqlAlchemyAuditoriaEscritorGateway:
    """AP-0028: adaptador SQL de escritura autonoma de asientos de auditoria.

    Implementa AuditoriaEscritorGateway (PEP 544). Persiste cada asiento en su propia sesion
    y transaccion, independiente de la operacion de negocio, de modo que el registro no
    dependa del exito o rollback de esta. DDL en sql/ap0028_audit_log.sql.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession] | None) -> None:
        self._session_factory: async_sessionmaker[AsyncSession] | None = session_factory

    async def guardar_async(self, registro: RegistroAuditoria) -> None:
        if self._session_factory is None:
            raise RuntimeError("Fabrica de sesiones no inicializada para auditoria")
        async with self._session_factory() as session:
            session.add(
                AuditLogModel(
                    user_id=registro.user_id,
                    usuario=registro.usuario,
                    accion=registro.accion,
                    entidad=registro.entidad,
                    entidad_id=registro.entidad_id,
                    detalle=registro.detalle,
                    ip_origen=registro.ip_origen,
                    resultado=registro.resultado,
                    creado_iso=registro.creado_iso,
                )
            )
            await session.commit()
