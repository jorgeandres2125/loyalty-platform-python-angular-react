from sqlalchemy import Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class AuditLogModel(Base):
    """AP-0028: tabla audit_log â€” historial de acciones de usuario (nuevo subsistema).

    Propiedad del nuevo sistema (no toca las tablas legacy auditor e historico). El instante
    se guarda en ISO 8601 (texto) para no depender de conversiones de fecha del proveedor.
    """

    __tablename__ = "audit_log"
    __table_args__ = (Index("IX_audit_log_user_fecha", "user_id", "creado_iso"),)

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column("user_id", Integer, nullable=True)
    usuario: Mapped[str] = mapped_column("usuario", String(100), default="")
    accion: Mapped[str] = mapped_column("accion", String(80))
    entidad: Mapped[str | None] = mapped_column("entidad", String(80), nullable=True)
    entidad_id: Mapped[str | None] = mapped_column("entidad_id", String(80), nullable=True)
    detalle: Mapped[str | None] = mapped_column("detalle", Text, nullable=True)
    ip_origen: Mapped[str | None] = mapped_column("ip_origen", String(64), nullable=True)
    resultado: Mapped[str] = mapped_column("resultado", String(20), default="exito")
    creado_iso: Mapped[str] = mapped_column("creado_iso", String(40), default="")
