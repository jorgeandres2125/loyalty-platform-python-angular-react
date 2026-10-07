from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class BancoModel(Base):
    __tablename__ = "bancos"

    # `tid` no es IDENTITY — el repositorio asigna MAX(tid)+1.
    tid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    codigo: Mapped[str | None] = mapped_column(String(10), nullable=True)
