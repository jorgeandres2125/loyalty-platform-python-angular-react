from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.registro_auditoria import RegistroAuditoria
from src.domain.value_objects.filtro_auditoria import FiltroAuditoria
from src.infrastructure.persistence.models.audit_log_model import AuditLogModel


class SqlAlchemyAuditoriaLectorRepo:
    """AP-0028: adaptador SQL de lectura del historial (tabla audit_log).

    Implementa AuditoriaLectorRepository (PEP 544). Filtra por usuario y aplica accion y
    rango de fechas ISO, ordenando por instante descendente. DDL en sql/ap0028_audit_log.sql.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def listar_por_usuario_async(
        self, user_id: int, filtro: FiltroAuditoria
    ) -> list[RegistroAuditoria]:
        stmt = select(AuditLogModel).where(AuditLogModel.user_id == user_id)
        if filtro.accion:
            stmt = stmt.where(AuditLogModel.accion == filtro.accion)
        if filtro.desde_iso:
            stmt = stmt.where(AuditLogModel.creado_iso >= filtro.desde_iso)
        if filtro.hasta_iso:
            stmt = stmt.where(AuditLogModel.creado_iso <= filtro.hasta_iso)
        stmt = stmt.order_by(AuditLogModel.creado_iso.desc())
        stmt = stmt.offset(filtro.offset).limit(filtro.limit)
        modelos = (await self._session.execute(stmt)).scalars().all()
        return [self._a_entidad(modelo) for modelo in modelos]

    async def contar_por_usuario_async(self, user_id: int, filtro: FiltroAuditoria) -> int:
        stmt = (
            select(func.count())
            .select_from(AuditLogModel)
            .where(AuditLogModel.user_id == user_id)
        )
        if filtro.accion:
            stmt = stmt.where(AuditLogModel.accion == filtro.accion)
        if filtro.desde_iso:
            stmt = stmt.where(AuditLogModel.creado_iso >= filtro.desde_iso)
        if filtro.hasta_iso:
            stmt = stmt.where(AuditLogModel.creado_iso <= filtro.hasta_iso)
        total = (await self._session.execute(stmt)).scalar_one()
        return int(total)

    @staticmethod
    def _a_entidad(model: AuditLogModel) -> RegistroAuditoria:
        return RegistroAuditoria(
            id=model.id,
            user_id=model.user_id,
            usuario=model.usuario,
            accion=model.accion,
            entidad=model.entidad,
            entidad_id=model.entidad_id,
            detalle=model.detalle,
            ip_origen=model.ip_origen,
            resultado=model.resultado,
            creado_iso=model.creado_iso,
        )
