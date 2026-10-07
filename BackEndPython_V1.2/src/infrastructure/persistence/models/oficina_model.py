from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class OficinaModel(Base):
    __tablename__ = "oficinas"

    cod_oficinas: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_oficinas: Mapped[int | None] = mapped_column(Integer)
    nom_oficinas: Mapped[str | None] = mapped_column(String(120))
    marca: Mapped[str | None] = mapped_column(String(45))
    regional: Mapped[str | None] = mapped_column(String(45))
    cpid: Mapped[int | None] = mapped_column(Integer)
    ind_activo: Mapped[bool | None] = mapped_column(Boolean)
