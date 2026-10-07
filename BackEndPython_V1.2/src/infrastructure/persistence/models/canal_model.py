from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class CanalModel(Base):
    __tablename__ = "canales"

    cod_canales: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom_canales: Mapped[str | None] = mapped_column(String(120))
    cpid: Mapped[int | None] = mapped_column(Integer)
    cspid: Mapped[int | None] = mapped_column(Integer)
    ind_activo: Mapped[bool | None] = mapped_column(Boolean)
    id_canales: Mapped[int] = mapped_column(Integer, nullable=False)
