from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from .perfil_contacto_model import PerfilContactoModel


class PerfilEmocionalModel(Base):
    __tablename__ = "users_perfil_emocional"

    # PK = FK 1:1 al perfil de contacto. Unificada a nvarchar(40) (ADR-02).
    numero_documento: Mapped[str] = mapped_column(
        String(40),
        ForeignKey("users_perfil_contacto.numero_documento", ondelete="CASCADE"),
        primary_key=True,
    )
    con_quien_vives: Mapped[str | None] = mapped_column(String(400))
    estado_civil: Mapped[str | None] = mapped_column(String(220))
    numero_hijos: Mapped[str | None] = mapped_column(String(220))
    info_hijos: Mapped[str | None] = mapped_column(String(2000))
    hobbies: Mapped[str | None] = mapped_column(String(2000))
    premios_gustaria_recibir: Mapped[str | None] = mapped_column(String(220))
    nivel_educativo: Mapped[str | None] = mapped_column(String(220))
    profesion: Mapped[str | None] = mapped_column(String(220))
    numero_mascotas: Mapped[str | None] = mapped_column(String(220))
    info_mascotas: Mapped[str | None] = mapped_column(String(2000))
    temas_a_profundizar: Mapped[str | None] = mapped_column(String(240))
    acepto_terminos_y_condiciones: Mapped[int | None] = mapped_column(Integer)
    comisionista_programa_id: Mapped[int | None] = mapped_column(SmallInteger)
    info_premios: Mapped[str | None] = mapped_column(String(300))
    propositos_familiares: Mapped[str | None] = mapped_column(String(2000))
    propositos_financieros: Mapped[str | None] = mapped_column(String(2000))
    propositos_diversion: Mapped[str | None] = mapped_column(String(2000))
    propositos_salud: Mapped[str | None] = mapped_column(String(2000))
    propositos_competencias: Mapped[str | None] = mapped_column(String(2000))

    contacto: Mapped[PerfilContactoModel] = relationship(
        "PerfilContactoModel", lazy="select"
    )
