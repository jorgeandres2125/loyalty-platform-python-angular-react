from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class HistoricoCorreoModel(Base):
    """Log de correos enviados. Reusa la forma del legado; en 2019 se le añade
    PRIMARY KEY en `hc_uid` (ADR-07) — aquí se crea ya con la constraint."""

    __tablename__ = "historico_correo"

    hc_uid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo_correo: Mapped[str | None] = mapped_column(String(50))
    usuario_envio: Mapped[str | None] = mapped_column(String(100))
    usuario_destino: Mapped[str | None] = mapped_column(String(254))
    fecha: Mapped[datetime | None] = mapped_column(DateTime)
    enviado: Mapped[bool | None] = mapped_column(Boolean)
