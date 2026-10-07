-- ============================================================================
-- Migration: 20260519_0005 — Grant DASHBOARD a roles comisionista (rid=4) y
--                            comisionista consumo (rid=14). Solo puede_ver.
-- Idempotente: NOT EXISTS en (rid, module_id).
-- ============================================================================

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

BEGIN TRANSACTION;
GO

INSERT INTO dbo.frontend_modules_permissions
    (rid, module_id, puede_ver, puede_crear, puede_editar, puede_eliminar, puede_exportar, puede_aprobar)
SELECT r.rid, fm.module_id,
       1, 0, 0, 0, 0, 0
FROM dbo.role r
CROSS JOIN dbo.frontend_modules fm
WHERE r.name IN ('comisionista', 'comisionista consumo')
  AND fm.module_code = 'DASHBOARD'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.frontend_modules_permissions fmp
      WHERE fmp.rid = r.rid AND fmp.module_id = fm.module_id
  );
GO

COMMIT TRANSACTION;
GO

PRINT '✓ DASHBOARD otorgado (puede_ver=1) a comisionista y comisionista consumo';
GO
