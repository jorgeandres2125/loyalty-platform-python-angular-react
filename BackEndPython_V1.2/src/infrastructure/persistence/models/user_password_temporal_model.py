from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class UserPasswordTemporalModel(Base):
    """AP-0046, AP-0047 y AP-0048: tabla user_password_temporal.

    Propiedad del nuevo sistema (no toca dbo.users, de Drupal). Cada emision es una
    fila nueva: la tabla es a la vez credencial temporal vigente y evidencia de
    auditoria de emisiones (origen completo). El vencimiento es derivado de
    expira_iso; los estados persistidos son activa, usada, consumida y reemplazada.
    """

    __tablename__ = "user_password_temporal"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    uid: Mapped[int] = mapped_column("uid", Integer, nullable=False, index=True)
    hash_temporal: Mapped[str] = mapped_column("hash_temporal", String(255), nullable=False)
    emitida_por_uid: Mapped[int] = mapped_column("emitida_por_uid", Integer, nullable=False)
    emitida_por_usuario: Mapped[str] = mapped_column(
        "emitida_por_usuario", String(120), nullable=False
    )
    origen: Mapped[str] = mapped_column("origen", String(20), nullable=False)
    motivo: Mapped[str | None] = mapped_column("motivo", String(200), nullable=True)
    ip_emision: Mapped[str | None] = mapped_column("ip_emision", String(64), nullable=True)
    emitida_iso: Mapped[str] = mapped_column("emitida_iso", String(40), nullable=False)
    expira_iso: Mapped[str] = mapped_column("expira_iso", String(40), nullable=False)
    usada_iso: Mapped[str | None] = mapped_column("usada_iso", String(40), nullable=True)
    consumida_iso: Mapped[str | None] = mapped_column(
        "consumida_iso", String(40), nullable=True
    )
    estado: Mapped[str] = mapped_column("estado", String(20), nullable=False)
