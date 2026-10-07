from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class UserPasswordHistoryModel(Base):
    """AP-0041: tabla user_password_history -- hashes de contrasenas usadas por usuario.

    Propiedad del nuevo sistema (no toca dbo.users, de Drupal). Guarda cada hash usado
    para impedir la reutilizacion de las ultimas N. Se poda a N por usuario.
    """

    __tablename__ = "user_password_history"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    uid: Mapped[int] = mapped_column("uid", Integer, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column("password_hash", String(255), nullable=False)
    creado_iso: Mapped[str] = mapped_column("creado_iso", String(40), nullable=False)
