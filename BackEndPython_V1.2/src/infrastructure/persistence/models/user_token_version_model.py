from datetime import datetime

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class UserTokenVersionModel(Base):
    """AP-0021: tabla user_token_version â€” version de credencial por usuario.

    Propiedad del nuevo sistema (no toca dbo.users). Incrementar token_version invalida
    de golpe todas las sesiones vivas del usuario (cambio de contrasena, cierre global,
    deshabilitacion).
    """

    __tablename__ = "user_token_version"

    uid: Mapped[int] = mapped_column("uid", Integer, primary_key=True)
    token_version: Mapped[int] = mapped_column("token_version", Integer, default=1)
    updated_at: Mapped[datetime | None] = mapped_column("updated_at", DateTime, nullable=True)
