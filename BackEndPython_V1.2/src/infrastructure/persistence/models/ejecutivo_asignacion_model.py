from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class EjecutivoAsignacionModel(Base):
    """Tabla users_ejecutivos — ejecutivos operacionales."""
    __tablename__ = "users_ejecutivos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo_documento: Mapped[str | None] = mapped_column(String(10), nullable=True)
    numero_documento: Mapped[str] = mapped_column(String(40), nullable=False)
    nombre_completo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    codigo_ejecutivo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    celular: Mapped[str | None] = mapped_column(String(36), nullable=True)
    perfil: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    estado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
