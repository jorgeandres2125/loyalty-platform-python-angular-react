from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.base import Base
from src.infrastructure.persistence.models.drupal_rol_model import DrupalRolModel


class DrupalUserRolModel(Base):
    """Mapea dbo.users_roles del snapshot Drupal 7."""
    __tablename__ = "users_roles"

    # uid alineado a Integer para casar con users.uid (int) y permitir el FK.
    uid: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.uid", ondelete="CASCADE"), primary_key=True
    )
    rid: Mapped[int] = mapped_column(
        Integer, ForeignKey("role.rid", ondelete="CASCADE"), primary_key=True
    )

    rol: Mapped["DrupalRolModel"] = relationship(
        "DrupalRolModel",
        primaryjoin="DrupalUserRolModel.rid == DrupalRolModel.rid",
        foreign_keys="DrupalUserRolModel.rid",
        lazy="selectin",
    )
