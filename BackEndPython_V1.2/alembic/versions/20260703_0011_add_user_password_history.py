"""Add user_password_history (AP-0041): no reutilizar las ultimas 24 contrasenas.

Crea la tabla lateral user_password_history en sufi_db. No toca dbo.users (Drupal).

Revision ID: 20260703_0011
Revises: 20260703_0010
Create Date: 2026-07-03
"""
from __future__ import annotations

from typing import Final

import sqlalchemy as sa

from alembic import op

revision: Final[str] = "20260703_0011"
down_revision: Final[str | None] = "20260703_0010"
branch_labels: Final[str | None] = None
depends_on: Final[str | None] = None


def upgrade() -> None:
    op.create_table(
        "user_password_history",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("uid", sa.Integer, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("creado_iso", sa.String(40), nullable=False),
    )
    op.create_index(
        "IX_user_password_history_uid_fecha",
        "user_password_history",
        ["uid", "creado_iso"],
    )


def downgrade() -> None:
    op.drop_index(
        "IX_user_password_history_uid_fecha", table_name="user_password_history"
    )
    op.drop_table("user_password_history")
