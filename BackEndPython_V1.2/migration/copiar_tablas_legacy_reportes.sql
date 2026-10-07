-- ============================================================================
-- copiar_tablas_legacy_reportes.sql
-- ----------------------------------------------------------------------------
-- sufi_db (esquema normalizado, dirigido por modelos SQLAlchemy) NO incluye las
-- tablas de referencia legacy que el generador de reportes consulta por SQL
-- crudo (no tienen modelo, por eso migrate_schema.py no las crea):
--
--   * users_migracion          (mainframe L222*, FIRMA_CONTRATO, ARL/EPS/AFP)
--   * taxonomy_term_data       (nombres de ARL/EPS/AFP/banco por tid)
--   * comisionistas_sufi_migrado (reporte "Usuarios migrados", L111*)
--
-- Sin ellas los reportes fallan con "Invalid object name". Este script las copia
-- desde sufiatulado (misma instancia) y es idempotente.
--
-- Colación: sufi_db = Modern_Spanish_CI_AS, sufiatulado = SQL_Latin1_General_CP1.
-- SELECT INTO preserva la colación de origen; solo users_migracion.L222NID se une
-- a una columna nvarchar de sufi_db (uc.numero_documento), así que se realinea su
-- colación para evitar el conflicto en el JOIN. taxonomy_term_data se une solo por
-- tid (int) y comisionistas_sufi_migrado no tiene joins → no requieren ajuste.
--
-- Ejecutar:
--   sqlcmd -S "127.0.0.1,1433" -U sa -P "<pwd>" -d sufi_db -i copiar_tablas_legacy_reportes.sql
-- ============================================================================
SET NOCOUNT ON;

IF OBJECT_ID('dbo.users_migracion') IS NULL
    SELECT * INTO dbo.users_migracion FROM sufiatulado.dbo.users_migracion;

IF COL_LENGTH('dbo.users_migracion', 'L222NID') IS NOT NULL
    ALTER TABLE dbo.users_migracion
        ALTER COLUMN L222NID nvarchar(100) COLLATE Modern_Spanish_CI_AS;

IF OBJECT_ID('dbo.taxonomy_term_data') IS NULL
    SELECT * INTO dbo.taxonomy_term_data FROM sufiatulado.dbo.taxonomy_term_data;

IF OBJECT_ID('dbo.comisionistas_sufi_migrado') IS NULL
    SELECT * INTO dbo.comisionistas_sufi_migrado FROM sufiatulado.dbo.comisionistas_sufi_migrado;

SELECT 'users_migracion' AS tabla, COUNT(*) AS filas FROM dbo.users_migracion
UNION ALL SELECT 'taxonomy_term_data', COUNT(*) FROM dbo.taxonomy_term_data
UNION ALL SELECT 'comisionistas_sufi_migrado', COUNT(*) FROM dbo.comisionistas_sufi_migrado;
