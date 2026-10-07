from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from .comisionista_programa_model import ComisionistaProgramaModel


class ComisionistaSubprogramaModel(Base):
    """Tabla comisionistas_subprograma."""
    __tablename__ = "comisionistas_subprograma"

    cspid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cspid_nombre: Mapped[str | None] = mapped_column(String(45))
    # FK al programa padre (1=Movilidad, 2=Consumo). SET NULL si se borra el programa.
    cpid: Mapped[int | None] = mapped_column(
        SmallInteger,
        ForeignKey("comisionistas_programa.cpid", ondelete="SET NULL"),
        index=True,
    )

    programa: Mapped[ComisionistaProgramaModel | None] = relationship(
        "ComisionistaProgramaModel", lazy="select"
    )
