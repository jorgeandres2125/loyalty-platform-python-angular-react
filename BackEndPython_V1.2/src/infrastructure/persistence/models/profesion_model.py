from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class ProfesionModel(Base):
    __tablename__ = "taxonomia_profesion"

    # `tid` no es IDENTITY — el repositorio asigna MAX(tid)+1.
    tid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    nombre: Mapped[str] = mapped_column(String(220), nullable=False)
