from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class UserLockoutModel(Base):
    """AP-0009: tabla user_lockout â€” estado de bloqueo por intentos fallidos de login.

    Propiedad del nuevo sistema (no toca dbo.users, que es de Drupal). Indexada por la
    clave de cuenta (nombre de usuario normalizado). Los instantes se guardan en
    segundos epoch para no depender del reloj monotono del proceso.
    """

    __tablename__ = "user_lockout"

    clave: Mapped[str] = mapped_column("clave", String(120), primary_key=True)
    conteo_fallos: Mapped[int] = mapped_column("conteo_fallos", Integer, default=0)
    bloqueada: Mapped[bool] = mapped_column("bloqueada", Boolean, default=False)
    bloqueada_en_epoch: Mapped[float] = mapped_column(
        "bloqueada_en_epoch", Float, default=0.0
    )
    expira_en_epoch: Mapped[float] = mapped_column("expira_en_epoch", Float, default=0.0)
    motivo: Mapped[str] = mapped_column("motivo", String(400), default="")
