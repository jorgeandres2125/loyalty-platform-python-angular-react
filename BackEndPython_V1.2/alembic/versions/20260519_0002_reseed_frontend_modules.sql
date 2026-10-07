-- ============================================================================
-- Migration: 20260519_0002 — Reseed frontend_modules (catálogo final inicial)
-- ----------------------------------------------------------------------------
-- Reemplaza el seed placeholder de 20260515_0001 por los 9 módulos reales del
-- SPA actual (sin jerarquía padre/hijo). Sólo el rol "administrator" recibe
-- los 6 flags en todos los módulos.
-- ============================================================================

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

BEGIN TRANSACTION;
GO

-- ── 1. Limpieza ────────────────────────────────────────────────────────────
DELETE FROM dbo.frontend_modules_permissions;
DELETE FROM dbo.frontend_modules;
DBCC CHECKIDENT ('dbo.frontend_modules_permissions', RESEED, 0);
DBCC CHECKIDENT ('dbo.frontend_modules',             RESEED, 0);
GO

-- ── 2. Seed: 9 módulos planos (sin module_padre_id) ───────────────────────
INSERT INTO dbo.frontend_modules
    (module_code, nombre, ruta, icono, module_padre_id, orden, activo)
VALUES
    ('DASHBOARD',        N'Dashboard',        '/dashboard',        'bi-speedometer2',           NULL, 10, 1),
    ('ASESOR_CONSUMO',   N'Asesor Consumo',   '/asesor-consumo',   'bi-bag-fill',               NULL, 20, 1),
    ('ASESOR_MOVILIDAD', N'Asesor Movilidad', '/asesor-movilidad', 'bi-car-front-fill',         NULL, 30, 1),
    ('SAPIN',            N'SAPIN',            '/sapin',            'bi-gift-fill',              NULL, 40, 1),
    ('REPORTES',         N'Reportes',         '/reportes',         'bi-file-earmark-bar-graph', NULL, 50, 1),
    ('EJECUTIVOS',       N'Ejecutivos',       '/ejecutivos',       'bi-person-badge-fill',      NULL, 60, 1),
    ('CANALES',          N'Canales',          '/canales',          'bi-diagram-3-fill',         NULL, 70, 1),
    ('OFICINAS',         N'Oficinas',         '/oficinas',         'bi-building',               NULL, 80, 1),
    ('PANEL_CONTROL',    N'Panel de Control', '/panel-control',    'bi-sliders',                NULL, 90, 1);
GO

-- ── 3. Grants completos sólo para "administrator" ─────────────────────────
INSERT INTO dbo.frontend_modules_permissions
    (rid, module_id, puede_ver, puede_crear, puede_editar, puede_eliminar, puede_exportar, puede_aprobar)
SELECT r.rid, fm.module_id, 1, 1, 1, 1, 1, 1
FROM dbo.role r
CROSS JOIN dbo.frontend_modules fm
WHERE r.name = 'administrator';
GO

COMMIT TRANSACTION;
GO

PRINT '✓ frontend_modules re-sembrado: 9 módulos planos, administrator con acceso total';
GO
