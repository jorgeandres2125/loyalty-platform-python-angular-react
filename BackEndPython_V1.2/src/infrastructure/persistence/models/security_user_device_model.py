from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class SecurityUserDeviceModel(Base):
    """AP-0014: tabla SECURITY_USER_DEVICE â€” dispositivo por usuario (nuevo sistema).

    Propiedad del nuevo sistema (no toca dbo.users). Los instantes se guardan como texto
    ISO 8601 para no depender de conversiones de fecha del proveedor.
    """

    __tablename__ = "SECURITY_USER_DEVICE"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True, autoincrement=True)
    uid: Mapped[int] = mapped_column("USER_ID", Integer)
    device_hash: Mapped[str] = mapped_column("DEVICE_HASH", String(128))
    device_name: Mapped[str] = mapped_column("DEVICE_NAME", String(200), default="")
    user_agent: Mapped[str] = mapped_column("USER_AGENT", String(512), default="")
    first_login_iso: Mapped[str] = mapped_column("FIRST_LOGIN", String(40), default="")
    last_login_iso: Mapped[str] = mapped_column("LAST_LOGIN", String(40), default="")
    veces_visto: Mapped[int] = mapped_column("VECES_VISTO", Integer, default=1)
    trusted: Mapped[bool] = mapped_column("TRUSTED", Boolean, default=False)
