"""Add user_password_temporal (AP-0046, AP-0047, AP-0048): contrasenas temporales.

Crea la tabla lateral user_password_temporal en sufi_db. No toca dbo.users (Drupal).
Guarda hash bcrypt de la temporal, origen completo de la emision (AP-0047), vigencia
de 120 minutos (AP-0048) y marcas de primer uso y consumo (AP-0046).

Revision ID: 20260703_0012
Revises: 20260703_0011
Create Date: 2026-07-06
"""
from __future__ import annotations

from typing import Final

import sqlalchemy as sa

from alembic import op

revision: Final[str] = "20260703_0012"
down_revision: Final[str | None] = "20260703_0011"
branch_labels: Final[str | None] = None
depends_on: Final[str | None] = None


def upgrade() -> None:
    op.create_table(
        "user_password_temporal",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("uid", sa.Integer, nullable=False),
        sa.Column("hash_temporal", sa.String(255), nullable=False),
        sa.Column("emitida_por_uid", sa.Integer, nullable=False),
        sa.Column("emitida_por_usuario", sa.String(120), nullable=False),
        sa.Column("origen", sa.String(20), nullable=False),
        sa.Column("motivo", sa.String(200), nullable=True),
        sa.Column("ip_emision", sa.String(64), nullable=True),
        sa.Column("emitida_iso", sa.String(40), nullable=False),
        sa.Column("expira_iso", sa.String(40), nullable=False),
        sa.Column("usada_iso", sa.String(40), nullable=True),
        sa.Column("consumida_iso", sa.String(40), nullable=True),
        sa.Column("estado", sa.String(20), nullable=False),
    )
    op.create_index(
        "IX_user_password_temporal_uid_estado",
        "user_password_temporal",
        ["uid", "estado"],
    )


def downgrade() -> None:
    op.drop_index(
        "IX_user_password_temporal_uid_estado", table_name="user_password_temporal"
    )
    op.drop_table("user_password_temporal")
