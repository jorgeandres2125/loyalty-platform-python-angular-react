from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class EjecutivoCatalogoModel(Base):
    """Tabla Ejecutivos (capital E) — importación legacy del mainframe. Columnas con espacios.

    'Usuario Asesor' NO es único en el legacy: la tabla es un mapeo asesor→comisionista
    (1 asesor : N comisionistas). Se usa un PK surrogado 'id' y se indexa el asesor.
    """
    __tablename__ = "Ejecutivos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_asesor: Mapped[str] = mapped_column("Usuario Asesor", String(60), index=True)
    email_asesor: Mapped[str | None] = mapped_column("E-mail Asesor", String(254))
    usuario_comisionista: Mapped[str | None] = mapped_column("Usuario Comisionista", Text)
    email_comisionista: Mapped[str | None] = mapped_column("E-mail Comisinista", Text)
    nombre_comisionista: Mapped[str | None] = mapped_column("Nombre Comisionista", Text)
    fecha_registro: Mapped[datetime | None] = mapped_column("Fecha Registro", DateTime)
