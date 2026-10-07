from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class UserAccountLockModel(Base):
    """AP-0157: tabla user_account_lock -- estado de bloqueo DURO por cuenta.

    Propiedad del nuevo sistema (no toca dbo.users, que es de Drupal). Indexada por uid.
    Independiente de user_lockout (bloqueo suave, AP-0009): ambos pueden coexistir. El
    bloqueo duro no expira; el instante de bloqueo se guarda en segundos epoch.
    """

    __tablename__ = "user_account_lock"

    uid: Mapped[int] = mapped_column("uid", Integer, primary_key=True)
    activo: Mapped[bool] = mapped_column("activo", Boolean, default=True)
    motivo: Mapped[str] = mapped_column("motivo", String(400), default="")
    bloqueado_en_epoch: Mapped[float] = mapped_column(
        "bloqueado_en_epoch", Float, default=0.0
    )
    bloqueado_por_uid: Mapped[int] = mapped_column("bloqueado_por_uid", Integer, default=0)
