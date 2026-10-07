from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class FrontendModuleModel(Base):
    """Catálogo plano de módulos del frontend (RBAC).

    Cada módulo tiene un código estable (UPPER_SNAKE_CASE) usado en JWT y middleware.
    No hay jerarquía padre/hijo: el SPA es una lista plana de 9 módulos.
    """
    __tablename__ = "frontend_modules"

    module_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module_code: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(400), nullable=True)
    icono: Mapped[str | None] = mapped_column(String(60), nullable=True)
    ruta: Mapped[str | None] = mapped_column(String(200), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    created: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("SYSUTCDATETIME()")
    )
    changed: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("SYSUTCDATETIME()")
    )
