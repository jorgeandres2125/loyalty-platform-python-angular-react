-- ============================================================================
-- Migration: 20260519_0003 — Drop frontend_modules.module_padre_id
-- ----------------------------------------------------------------------------
-- Decisión de diseño: no se necesita jerarquía padre/hijo en el catálogo de
-- módulos del SPA (9 módulos planos). Se eliminan la FK, el índice y la columna.
-- Idempotente: chequea existencia antes de borrar.
-- ============================================================================

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

BEGIN TRANSACTION;
GO

-- ── 1. FK self-referencial ────────────────────────────────────────────────
IF EXISTS (
    SELECT 1 FROM sys.foreign_keys
    WHERE name = 'fk_frontend_modules_padre'
      AND parent_object_id = OBJECT_ID('dbo.frontend_modules')
)
BEGIN
    ALTER TABLE dbo.frontend_modules DROP CONSTRAINT fk_frontend_modules_padre;
END
GO

-- ── 2. Índice sobre module_padre_id ───────────────────────────────────────
IF EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'ix_frontend_modules_padre'
      AND object_id = OBJECT_ID('dbo.frontend_modules')
)
BEGIN
    DROP INDEX ix_frontend_modules_padre ON dbo.frontend_modules;
END
GO

-- ── 3. Columna module_padre_id ────────────────────────────────────────────
IF EXISTS (
    SELECT 1 FROM sys.columns
    WHERE name = 'module_padre_id'
      AND object_id = OBJECT_ID('dbo.frontend_modules')
)
BEGIN
    ALTER TABLE dbo.frontend_modules DROP COLUMN module_padre_id;
END
GO

COMMIT TRANSACTION;
GO

PRINT '✓ frontend_modules.module_padre_id eliminado (FK + índice + columna)';
GO
