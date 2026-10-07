from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from .perfil_contacto_model import PerfilContactoModel


class DocumentoModel(Base):
    """Tabla user_documento — tipo: 4=Cédula, 5=RUT, 6=Contrato."""
    __tablename__ = "user_documento"

    did: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # FK 1:N al perfil de contacto. Origen legacy es numeric → se castea a
    # nvarchar(40) en la copia. Nullable: si no hay padre se deja NULL.
    numero_documento: Mapped[str | None] = mapped_column(
        String(40),
        ForeignKey("users_perfil_contacto.numero_documento", ondelete="SET NULL"),
        index=True,
    )
    nombre: Mapped[str | None] = mapped_column(String(50))
    estado: Mapped[str | None] = mapped_column(String(20))
    version: Mapped[int | None] = mapped_column(Integer)
    fecha: Mapped[datetime | None] = mapped_column(DateTime)
    tipo: Mapped[int | None] = mapped_column(Integer)

    contacto: Mapped[PerfilContactoModel | None] = relationship(
        "PerfilContactoModel", lazy="select"
    )
