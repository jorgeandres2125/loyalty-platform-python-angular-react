from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class AesPasswordModel(Base):
    """Tabla aes_passwords — contraseñas cifradas AES-256-CBC del sistema legacy."""
    __tablename__ = "aes_passwords"

    uid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    pass_: Mapped[str] = mapped_column("pass", String(128), nullable=False)
