from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from .canal_model import CanalModel
    from .oficina_model import OficinaModel


class CanalOficinaModel(Base):
    """Tabla canales_oficinas — relación canal ↔ oficina."""
    __tablename__ = "canales_oficinas"

    cod_canales_oficinas: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cod_canales: Mapped[int | None] = mapped_column(
        ForeignKey("canales.cod_canales", ondelete="CASCADE"), index=True
    )
    cod_oficinas: Mapped[int | None] = mapped_column(
        ForeignKey("oficinas.cod_oficinas", ondelete="CASCADE"), index=True
    )

    canal: Mapped[CanalModel | None] = relationship("CanalModel", lazy="select")
    oficina: Mapped[OficinaModel | None] = relationship("OficinaModel", lazy="select")
