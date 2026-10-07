-- ============================================================================
-- Migration: 20260519_0004 — Módulos "Perfil" + grants para comisionistas
-- ----------------------------------------------------------------------------
-- Crea dos módulos: PERFIL_COMISIONISTA_MOVILIDAD y PERFIL_COMISIONISTA_CONSUMO.
-- Ambos llevan `nombre = 'Perfil'`; cada rol verá solo el que le corresponde.
--
-- Grants:
--   • comisionista          (rid=4)  → PERFIL_COMISIONISTA_MOVILIDAD, SAPIN, PANEL_CONTROL
--   • comisionista consumo  (rid=14) → PERFIL_COMISIONISTA_CONSUMO,   SAPIN, PANEL_CONTROL
--
-- Idempotente: chequea existencia antes de insertar.
-- ============================================================================

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

BEGIN TRANSACTION;
GO

-- ── 1. Catálogo: dos módulos "Perfil" ─────────────────────────────────────
;WITH seed AS (
    SELECT * FROM (VALUES
        ('PERFIL_COMISIONISTA_MOVILIDAD', N'Perfil', '/perfil-movilidad', 'bi-person-circle', 15),
        ('PERFIL_COMISIONISTA_CONSUMO',   N'Perfil', '/perfil-consumo',   'bi-person-circle', 25)
    ) AS v(code, nombre, ruta, icono, orden)
)
INSERT INTO dbo.frontend_modules (module_code, nombre, ruta, icono, orden, activo)
SELECT s.code, s.nombre, s.ruta, s.icono, s.orden, 1
FROM seed s
WHERE NOT EXISTS (SELECT 1 FROM dbo.frontend_modules fm WHERE fm.module_code = s.code);
GO

-- ── 2. Grants: comisionista (rid=4) → MOVILIDAD + SAPIN + PANEL_CONTROL ──
INSERT INTO dbo.frontend_modules_permissions
    (rid, module_id, puede_ver, puede_crear, puede_editar, puede_eliminar, puede_exportar, puede_aprobar)
SELECT r.rid, fm.module_id,
       1 AS puede_ver,
       0 AS puede_crear,
       1 AS puede_editar,
       0 AS puede_eliminar,
       0 AS puede_exportar,
       0 AS puede_aprobar
FROM dbo.role r
CROSS JOIN dbo.frontend_modules fm
WHERE r.name = 'comisionista'
  AND fm.module_code IN ('PERFIL_COMISIONISTA_MOVILIDAD', 'SAPIN', 'PANEL_CONTROL')
  AND NOT EXISTS (
      SELECT 1 FROM dbo.frontend_modules_permissions fmp
      WHERE fmp.rid = r.rid AND fmp.module_id = fm.module_id
  );
GO

-- ── 3. Grants: comisionista consumo (rid=14) → CONSUMO + SAPIN + PANEL_CONTROL
INSERT INTO dbo.frontend_modules_permissions
    (rid, module_id, puede_ver, puede_crear, puede_editar, puede_eliminar, puede_exportar, puede_aprobar)
SELECT r.rid, fm.module_id,
       1 AS puede_ver,
       0 AS puede_crear,
       1 AS puede_editar,
       0 AS puede_eliminar,
       0 AS puede_exportar,
       0 AS puede_aprobar
FROM dbo.role r
CROSS JOIN dbo.frontend_modules fm
WHERE r.name = 'comisionista consumo'
  AND fm.module_code IN ('PERFIL_COMISIONISTA_CONSUMO', 'SAPIN', 'PANEL_CONTROL')
  AND NOT EXISTS (
      SELECT 1 FROM dbo.frontend_modules_permissions fmp
      WHERE fmp.rid = r.rid AND fmp.module_id = fm.module_id
  );
GO

COMMIT TRANSACTION;
GO

PRINT '✓ Módulos PERFIL_* creados y grants aplicados a comisionista / comisionista consumo';
GO
