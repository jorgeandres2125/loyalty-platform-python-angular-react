"""Add frontend_modules + frontend_modules_permissions (RBAC granular).

Revision ID: 20260515_0001
Revises:
Create Date: 2026-05-15
"""
from __future__ import annotations

from typing import Final

import sqlalchemy as sa
from alembic import op

revision: Final[str] = "20260515_0001"
down_revision: Final[str | None] = None
branch_labels: Final[str | None] = None
depends_on: Final[str | None] = None


# ── Catálogo inicial: 9 módulos planos del SPA ────────────────────────────────
# Cada item: (module_code, nombre, ruta, icono, orden)
SEED_MODULES: Final[list[tuple[str, str, str, str, int]]] = [
    ("DASHBOARD",        "Dashboard",        "/dashboard",        "bi-speedometer2",           10),
    ("ASESOR_CONSUMO",   "Asesor Consumo",   "/asesor-consumo",   "bi-bag-fill",               20),
    ("ASESOR_MOVILIDAD", "Asesor Movilidad", "/asesor-movilidad", "bi-car-front-fill",         30),
    ("SAPIN",            "SAPIN",            "/sapin",            "bi-gift-fill",              40),
    ("REPORTES",         "Reportes",         "/reportes",         "bi-file-earmark-bar-graph", 50),
    ("EJECUTIVOS",       "Ejecutivos",       "/ejecutivos",       "bi-person-badge-fill",      60),
    ("CANALES",          "Canales",          "/canales",          "bi-diagram-3-fill",         70),
    ("OFICINAS",         "Oficinas",         "/oficinas",         "bi-building",               80),
    ("PANEL_CONTROL",    "Panel de Control", "/panel-control",    "bi-sliders",                90),
]


def upgrade() -> None:
    # ── Tabla: frontend_modules ──────────────────────────────────────────────
    op.create_table(
        "frontend_modules",
        sa.Column("module_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("module_code", sa.String(60), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("descripcion", sa.String(400), nullable=True),
        sa.Column("icono", sa.String(60), nullable=True),
        sa.Column("ruta", sa.String(200), nullable=True),
        sa.Column("orden", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("activo", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column("created", sa.DateTime, nullable=False, server_default=sa.text("SYSUTCDATETIME()")),
        sa.Column("changed", sa.DateTime, nullable=False, server_default=sa.text("SYSUTCDATETIME()")),
        sa.UniqueConstraint("module_code", name="uq_frontend_modules_code"),
    )
    op.create_index("ix_frontend_modules_activo_orden", "frontend_modules", ["activo", "orden"])

    # ── Tabla: frontend_modules_permissions ──────────────────────────────────
    op.create_table(
        "frontend_modules_permissions",
        sa.Column("permission_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "rid",
            sa.Integer,
            sa.ForeignKey("role.rid", name="fk_fmp_role", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "module_id",
            sa.Integer,
            sa.ForeignKey("frontend_modules.module_id", name="fk_fmp_module", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("puede_ver",       sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column("puede_crear",     sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column("puede_editar",    sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column("puede_eliminar",  sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column("puede_exportar",  sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column("puede_aprobar",   sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column("created", sa.DateTime, nullable=False, server_default=sa.text("SYSUTCDATETIME()")),
        sa.Column("changed", sa.DateTime, nullable=False, server_default=sa.text("SYSUTCDATETIME()")),
        sa.UniqueConstraint("rid", "module_id", name="uq_fmp_role_module"),
    )
    op.create_index("ix_fmp_role", "frontend_modules_permissions", ["rid"])
    op.create_index("ix_fmp_module", "frontend_modules_permissions", ["module_id"])

    # ── Seed: 9 módulos planos (sin jerarquía padre/hijo) ───────────────────
    bind = op.get_bind()

    for code, nombre, ruta, icono, orden in SEED_MODULES:
        bind.execute(
            sa.text(
                """
                INSERT INTO frontend_modules (module_code, nombre, ruta, icono, orden, activo)
                VALUES (:code, :nombre, :ruta, :icono, :orden, 1)
                """
            ),
            {"code": code, "nombre": nombre, "ruta": ruta, "icono": icono, "orden": orden},
        )

    # ── Seed: grants completos sólo para "administrator" ────────────────────
    bind.execute(
        sa.text(
            """
            INSERT INTO frontend_modules_permissions
                (rid, module_id, puede_ver, puede_crear, puede_editar, puede_eliminar, puede_exportar, puede_aprobar)
            SELECT r.rid, fm.module_id, 1, 1, 1, 1, 1, 1
            FROM role r
            CROSS JOIN frontend_modules fm
            WHERE r.name = 'administrator'
            """
        )
    )


def downgrade() -> None:
    op.drop_index("ix_fmp_module", table_name="frontend_modules_permissions")
    op.drop_index("ix_fmp_role", table_name="frontend_modules_permissions")
    op.drop_table("frontend_modules_permissions")

    op.drop_index("ix_frontend_modules_activo_orden", table_name="frontend_modules")
    op.drop_table("frontend_modules")
