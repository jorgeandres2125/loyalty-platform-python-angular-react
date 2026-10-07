from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class AfpModel(Base):
    __tablename__ = "afp"

    # `tid` no es IDENTITY en SQL Server — el repositorio asigna MAX(tid)+1.
    # Sin `autoincrement=False`, SQLAlchemy emite `SET IDENTITY_INSERT afp ON`
    # en cada INSERT explícito y SQL Server rechaza con error 8106.
    tid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    nit: Mapped[str | None] = mapped_column(String(30), nullable=True)
