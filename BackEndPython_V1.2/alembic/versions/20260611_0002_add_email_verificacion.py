"""Add email verification (AP-0004): perfil flags + historico_correo.

Añade users_perfil_contacto.email_verificado / email_verificado_fecha y crea la
tabla historico_correo en sufi_db (solo existía en sufiatulado), ya con PRIMARY KEY
en hc_uid (ADR-07).

Revision ID: 20260611_0002
Revises: 20260515_0001
Create Date: 2026-06-11
"""
from __future__ import annotations

from typing import Final

import sqlalchemy as sa
from alembic import op

revision: Final[str] = "20260611_0002"
down_revision: Final[str | None] = "20260515_0001"
branch_labels: Final[str | None] = None
depends_on: Final[str | None] = None


def upgrade() -> None:
    # ── Banderas de verificación de correo en el perfil de contacto ──────────
    op.add_column(
        "users_perfil_contacto",
        sa.Column("email_verificado", sa.Boolean, nullable=True, server_default=sa.text("0")),
    )
    op.add_column(
        "users_perfil_contacto",
        sa.Column("email_verificado_fecha", sa.DateTime, nullable=True),
    )

    # ── Log de correos enviados (historico_correo) — con PK en hc_uid (ADR-07) ─
    op.create_table(
        "historico_correo",
        sa.Column("hc_uid", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("tipo_correo", sa.String(50), nullable=True),
        sa.Column("usuario_envio", sa.String(100), nullable=True),
        sa.Column("usuario_destino", sa.String(254), nullable=True),
        sa.Column("fecha", sa.DateTime, nullable=True),
        sa.Column("enviado", sa.Boolean, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("historico_correo")
    op.drop_column("users_perfil_contacto", "email_verificado_fecha")
    op.drop_column("users_perfil_contacto", "email_verificado")
