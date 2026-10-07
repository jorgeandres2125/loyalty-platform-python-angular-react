"""Add user_password_expiracion (AP-0037): reloj de vencimiento de contrasena.

Crea la tabla lateral user_password_expiracion en sufi_db para soportar el aviso
de vencimiento de contrasena con 7 dias de antelacion. No toca dbo.users (Drupal).

Revision ID: 20260703_0010
Revises: 20260703_0009
Create Date: 2026-07-03
"""
from __future__ import annotations

from typing import Final

import sqlalchemy as sa

from alembic import op

revision: Final[str] = "20260703_0010"
down_revision: Final[str | None] = "20260703_0009"
branch_labels: Final[str | None] = None
depends_on: Final[str | None] = None


def upgrade() -> None:
    op.create_table(
        "user_password_expiracion",
        sa.Column("uid", sa.Integer, primary_key=True, autoincrement=False),
        sa.Column("password_cambiado_en", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("user_password_expiracion")
