from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class UserPasswordExpiracionModel(Base):
    """AP-0037: tabla user_password_expiracion -- reloj de vencimiento por usuario.

    Propiedad del nuevo sistema (no toca dbo.users, de Drupal). Guarda el instante
    del ultimo cambio de contrasena; la vigencia configurada define el vencimiento.
    """

    __tablename__ = "user_password_expiracion"

    uid: Mapped[int] = mapped_column("uid", Integer, primary_key=True)
    password_cambiado_en: Mapped[datetime] = mapped_column(
        "password_cambiado_en", DateTime, nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        "updated_at", DateTime, nullable=True
    )
