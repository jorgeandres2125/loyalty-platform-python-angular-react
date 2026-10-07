-- AP-0028: tabla audit_log (historial de acciones de usuario) para SQL Server 2019.
-- Equivalente en T-SQL de la migracion Alembic 20260703_0009. No toca tablas legacy.
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'audit_log')
BEGIN
    CREATE TABLE dbo.audit_log (
        id          INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        user_id     INT NULL,
        usuario     NVARCHAR(100) NULL,
        accion      NVARCHAR(80) NOT NULL,
        entidad     NVARCHAR(80) NULL,
        entidad_id  NVARCHAR(80) NULL,
        detalle     NVARCHAR(MAX) NULL,
        ip_origen   NVARCHAR(64) NULL,
        resultado   NVARCHAR(20) NULL,
        creado_iso  NVARCHAR(40) NULL
    );
    CREATE INDEX IX_audit_log_user_fecha ON dbo.audit_log (user_id, creado_iso DESC);
END;
