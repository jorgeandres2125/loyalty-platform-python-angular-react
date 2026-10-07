from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class FrontendModulePermissionModel(Base):
    """Permisos por (rol, módulo) — RBAC granular.

    Una sola fila por par (rid, module_id); los flags se modifican, no se duplican filas.
    Semántica del usuario: unión (OR) de los permisos de todos sus roles.
    """
    __tablename__ = "frontend_modules_permissions"
    __table_args__ = (
        UniqueConstraint("rid", "module_id", name="uq_fmp_role_module"),
    )

    permission_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rid: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("role.rid", name="fk_fmp_role", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    module_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("frontend_modules.module_id", name="fk_fmp_module", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    puede_ver: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    puede_crear: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    puede_editar: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    puede_eliminar: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    puede_exportar: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    puede_aprobar: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    created: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("SYSUTCDATETIME()")
    )
    changed: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("SYSUTCDATETIME()")
    )
