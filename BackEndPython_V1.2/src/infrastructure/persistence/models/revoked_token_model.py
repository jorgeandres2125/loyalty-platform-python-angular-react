from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class RevokedTokenModel(Base):
    """AP-0021: tabla revoked_token â€” denylist de jti revocados (nuevo sistema).

    Cada fila vive hasta expira_en_epoch (la vida restante del token); un job de purga
    o el propio adaptador la retira despues.
    """

    __tablename__ = "revoked_token"

    jti: Mapped[str] = mapped_column("jti", String(64), primary_key=True)
    uid: Mapped[int] = mapped_column("uid", Integer, default=0)
    expira_en_epoch: Mapped[float] = mapped_column("expira_en_epoch", Float, default=0.0)
    motivo: Mapped[str] = mapped_column("motivo", String(40), default="logout")
