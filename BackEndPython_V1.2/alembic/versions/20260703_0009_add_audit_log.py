"""Add audit_log (AP-0028): historial de acciones de usuario.

Crea la tabla audit_log en sufi_db para el subsistema de auditoria consultable por el propio
usuario, con indice por (user_id, creado_iso). No toca las tablas legacy auditor e historico.

Revision ID: 20260703_0009
Revises: 20260611_0002
Create Date: 2026-07-03
"""
from __future__ import annotations

from typing import Final

import sqlalchemy as sa

from alembic import op

revision: Final[str] = "20260703_0009"
down_revision: Final[str | None] = "20260611_0002"
branch_labels: Final[str | None] = None
depends_on: Final[str | None] = None


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=True),
        sa.Column("usuario", sa.String(100), nullable=True),
        sa.Column("accion", sa.String(80), nullable=False),
        sa.Column("entidad", sa.String(80), nullable=True),
        sa.Column("entidad_id", sa.String(80), nullable=True),
        sa.Column("detalle", sa.Text, nullable=True),
        sa.Column("ip_origen", sa.String(64), nullable=True),
        sa.Column("resultado", sa.String(20), nullable=True),
        sa.Column("creado_iso", sa.String(40), nullable=True),
    )
    op.create_index("IX_audit_log_user_fecha", "audit_log", ["user_id", "creado_iso"])


def downgrade() -> None:
    op.drop_index("IX_audit_log_user_fecha", table_name="audit_log")
    op.drop_table("audit_log")
