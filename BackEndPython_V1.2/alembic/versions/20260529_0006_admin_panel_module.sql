-- ============================================================================
-- Migration: 20260529_0006 — Panel de Control (administración de catálogos)
-- ----------------------------------------------------------------------------
-- 1. Renombra el módulo PANEL_CONTROL → CONFIGURACIONES (era el panel de
--    configuración personal del comisionista — cambio de contraseña, etc.).
--    Los grants existentes a comisionista/comisionista_consumo se preservan
--    porque la FK es por module_id, no por module_code.
-- 2. Crea nuevo módulo PANEL_ADMIN ('Panel de Control') apuntando a
--    /admin/dashboard. Es el hub administrativo para CRUD de catálogos
--    maestros (AFP, ARL, EPS, Bancos, Departamentos, Ciudades, Programas,
--    Sub-programas, Taxonomía de profesión).
-- 3. Otorga TODOS los flags (ver/crear/editar/eliminar/exportar/aprobar) al
--    rol administrator (rid=3) sobre PANEL_ADMIN.
--
-- Idempotente: chequea existencia antes de insertar/actualizar.
-- ============================================================================

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

BEGIN TRANSACTION;
GO

-- ── 1. Renombrar el módulo PANEL_CONTROL → CONFIGURACIONES ───────────────────
UPDATE dbo.frontend_modules
SET module_code = 'CONFIGURACIONES',
    nombre      = N'Configuraciones',
    descripcion = N'Preferencias personales (cambio de contraseña, etc.)'
WHERE module_code = 'PANEL_CONTROL';
GO

-- ── 2. Insertar el nuevo módulo PANEL_ADMIN ──────────────────────────────────
INSERT INTO dbo.frontend_modules (module_code, nombre, descripcion, ruta, icono, orden, activo)
SELECT 'PANEL_ADMIN',
       N'Panel de Control',
       N'Administración de catálogos maestros del sistema',
       '/admin/dashboard',
       'bi-grid-3x3-gap-fill',
       95,
       1
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.frontend_modules WHERE module_code = 'PANEL_ADMIN'
);
GO

-- ── 3. CONFIGURACIONES sin ruta nav: acceso solo desde Panel de Control ────────
--    El módulo existe (para permisos por role), pero sin ruta no aparece en
--    la navegación dinámica del Topbar/Sidebar.
UPDATE dbo.frontend_modules
SET ruta = NULL
WHERE module_code = 'CONFIGURACIONES';
GO

-- ── 4. Grant completo (todos los flags) a administrator (rid=3) ──────────────
INSERT INTO dbo.frontend_modules_permissions
    (rid, module_id, puede_ver, puede_crear, puede_editar, puede_eliminar, puede_exportar, puede_aprobar)
SELECT r.rid, fm.module_id,
       1 AS puede_ver,
       1 AS puede_crear,
       1 AS puede_editar,
       1 AS puede_eliminar,
       1 AS puede_exportar,
       1 AS puede_aprobar
FROM dbo.role r
CROSS JOIN dbo.frontend_modules fm
WHERE r.name = 'administrator'
  AND fm.module_code = 'PANEL_ADMIN'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.frontend_modules_permissions fmp
      WHERE fmp.rid = r.rid AND fmp.module_id = fm.module_id
  );
GO

-- ── 5. Grant solo puede_ver a asesores consumo y movilidad ──────────────────
--    Pueden ver el Panel de Control (card de Cuenta); no tienen acceso
--    a catálogos maestros (eso lo bloquea el frontend con adminOnly=true).
INSERT INTO dbo.frontend_modules_permissions
    (rid, module_id, puede_ver, puede_crear, puede_editar, puede_eliminar, puede_exportar, puede_aprobar)
SELECT r.rid, fm.module_id,
       1 AS puede_ver,
       0, 0, 0, 0, 0
FROM dbo.role r
CROSS JOIN dbo.frontend_modules fm
WHERE fm.module_code = 'PANEL_ADMIN'
  AND r.rid IN (
      SELECT rid FROM dbo.role
      WHERE name IN ('asesor logistico','asesor comercial','asesor callcenter','asesor consumo')
  )
  AND NOT EXISTS (
      SELECT 1 FROM dbo.frontend_modules_permissions fmp
      WHERE fmp.rid = r.rid AND fmp.module_id = fm.module_id
  );
GO

COMMIT TRANSACTION;
GO

PRINT 'OK | PANEL_CONTROL→CONFIGURACIONES (sin ruta nav); PANEL_ADMIN creado y otorgado a administrator + asesores';
GO
