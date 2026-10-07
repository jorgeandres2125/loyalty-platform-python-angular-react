
from sqlalchemy import Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.base import Base
from src.infrastructure.persistence.models.drupal_user_rol_model import DrupalUserRolModel


class DrupalUserModel(Base):
    """Mapea dbo.users del snapshot Drupal 7 — tabla de origen para autenticación."""
    __tablename__ = "users"

    uid: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(60))
    mail: Mapped[str | None] = mapped_column(String(254))
    pass_: Mapped[str | None] = mapped_column("pass", String(128))
    new_pass: Mapped[str | None] = mapped_column("new_pass", String(128), nullable=True)
    status: Mapped[int | None] = mapped_column(SmallInteger)
    created: Mapped[int | None] = mapped_column(Integer)
    access: Mapped[int | None] = mapped_column(Integer)

    roles: Mapped[list["DrupalUserRolModel"]] = relationship(
        "DrupalUserRolModel",
        primaryjoin="DrupalUserModel.uid == DrupalUserRolModel.uid",
        foreign_keys="DrupalUserRolModel.uid",
        lazy="selectin",
    )
