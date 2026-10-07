from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class DrupalRolModel(Base):
    """Mapea dbo.role del snapshot Drupal 7."""
    __tablename__ = "role"

    rid: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
