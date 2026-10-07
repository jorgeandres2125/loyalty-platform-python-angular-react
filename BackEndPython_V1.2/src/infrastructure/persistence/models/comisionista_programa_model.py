from __future__ import annotations

from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class ComisionistaProgramaModel(Base):
    """Tabla comisionistas_programa — catálogo de programas (cpid es PK sin autoincremento)."""
    __tablename__ = "comisionistas_programa"

    cpid: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=False)
    cp_nombre: Mapped[str] = mapped_column(String(50), nullable=False)
