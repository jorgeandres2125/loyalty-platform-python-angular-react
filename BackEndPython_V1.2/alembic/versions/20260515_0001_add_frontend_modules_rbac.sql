-- ============================================================================
-- Migration: 20260515_0001 — Add frontend_modules + frontend_modules_permissions
-- Generated from alembic/versions/20260515_0001_add_frontend_modules_rbac.py
-- Idempotente: chequea existencia antes de crear.
-- ============================================================================

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

BEGIN TRANSACTION;
GO

-- ── Tabla: frontend_modules ─────────────────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'frontend_modules')
BEGIN
    CREATE TABLE dbo.frontend_modules (
        module_id        INT             IDENTITY(1,1) NOT NULL,
        module_code      NVARCHAR(60)    NOT NULL,
        nombre           NVARCHAR(120)   NOT NULL,
        descripcion      NVARCHAR(400)   NULL,
        icono            NVARCHAR(60)    NULL,
        ruta             NVARCHAR(200)   NULL,
        orden            INT             NOT NULL CONSTRAINT df_frontend_modules_orden  DEFAULT (0),
        activo           BIT             NOT NULL CONSTRAINT df_frontend_modules_activo DEFAULT (1),
        created          DATETIME2       NOT NULL CONSTRAINT df_frontend_modules_created DEFAULT (SYSUTCDATETIME()),
        changed          DATETIME2       NOT NULL CONSTRAINT df_frontend_modules_changed DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT pk_frontend_modules     PRIMARY KEY CLUSTERED (module_id),
        CONSTRAINT uq_frontend_modules_code UNIQUE (module_code)
    );

    CREATE INDEX ix_frontend_modules_activo_orden ON dbo.frontend_modules (activo, orden);
END
GO

-- ── Tabla: frontend_modules_permissions ────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'frontend_modules_permissions')
BEGIN
    CREATE TABLE dbo.frontend_modules_permissions (
        permission_id    INT       IDENTITY(1,1) NOT NULL,
        rid              INT       NOT NULL,
        module_id        INT       NOT NULL,
        puede_ver        BIT       NOT NULL CONSTRAINT df_fmp_puede_ver       DEFAULT (0),
        puede_crear      BIT       NOT NULL CONSTRAINT df_fmp_puede_crear     DEFAULT (0),
        puede_editar     BIT       NOT NULL CONSTRAINT df_fmp_puede_editar    DEFAULT (0),
        puede_eliminar   BIT       NOT NULL CONSTRAINT df_fmp_puede_eliminar  DEFAULT (0),
        puede_exportar   BIT       NOT NULL CONSTRAINT df_fmp_puede_exportar  DEFAULT (0),
        puede_aprobar    BIT       NOT NULL CONSTRAINT df_fmp_puede_aprobar   DEFAULT (0),
        created          DATETIME2 NOT NULL CONSTRAINT df_fmp_created DEFAULT (SYSUTCDATETIME()),
        changed          DATETIME2 NOT NULL CONSTRAINT df_fmp_changed DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT pk_frontend_modules_permissions PRIMARY KEY CLUSTERED (permission_id),
        CONSTRAINT uq_fmp_role_module UNIQUE (rid, module_id),
        CONSTRAINT fk_fmp_role   FOREIGN KEY (rid)       REFERENCES dbo.role (rid)              ON DELETE CASCADE,
        CONSTRAINT fk_fmp_module FOREIGN KEY (module_id) REFERENCES dbo.frontend_modules (module_id) ON DELETE CASCADE
    );

    CREATE INDEX ix_fmp_role   ON dbo.frontend_modules_permissions (rid);
    CREATE INDEX ix_fmp_module ON dbo.frontend_modules_permissions (module_id);
END
GO

-- ── Seed: catálogo de 9 módulos planos (idempotente por module_code) ──────
;WITH seed AS (
    SELECT * FROM (VALUES
        ('DASHBOARD',        N'Dashboard',        '/dashboard',        'bi-speedometer2',           10),
        ('ASESOR_CONSUMO',   N'Asesor Consumo',   '/asesor-consumo',   'bi-bag-fill',               20),
        ('ASESOR_MOVILIDAD', N'Asesor Movilidad', '/asesor-movilidad', 'bi-car-front-fill',         30),
        ('SAPIN',            N'SAPIN',            '/sapin',            'bi-gift-fill',              40),
        ('REPORTES',         N'Reportes',         '/reportes',         'bi-file-earmark-bar-graph', 50),
        ('EJECUTIVOS',       N'Ejecutivos',       '/ejecutivos',       'bi-person-badge-fill',      60),
        ('CANALES',          N'Canales',          '/canales',          'bi-diagram-3-fill',         70),
        ('OFICINAS',         N'Oficinas',         '/oficinas',         'bi-building',               80),
        ('PANEL_CONTROL',    N'Panel de Control', '/panel-control',    'bi-sliders',                90)
    ) AS v(code, nombre, ruta, icono, orden)
)
INSERT INTO dbo.frontend_modules (module_code, nombre, ruta, icono, orden, activo)
SELECT s.code, s.nombre, s.ruta, s.icono, s.orden, 1
FROM seed s
WHERE NOT EXISTS (SELECT 1 FROM dbo.frontend_modules fm WHERE fm.module_code = s.code);
GO

-- ── Seed: grants completos sólo para "administrator" ──────────────────────
INSERT INTO dbo.frontend_modules_permissions
    (rid, module_id, puede_ver, puede_crear, puede_editar, puede_eliminar, puede_exportar, puede_aprobar)
SELECT r.rid, fm.module_id, 1, 1, 1, 1, 1, 1
FROM dbo.role r
CROSS JOIN dbo.frontend_modules fm
WHERE r.name = 'administrator'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.frontend_modules_permissions fmp
      WHERE fmp.rid = r.rid AND fmp.module_id = fm.module_id
  );
GO

COMMIT TRANSACTION;
GO

PRINT '✓ frontend_modules + frontend_modules_permissions creadas y sembradas';
GO
