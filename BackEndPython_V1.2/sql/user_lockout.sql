-- AP-0009: tabla de estado de bloqueo de cuenta por intentos fallidos de login.
-- Propiedad del nuevo sistema (no modifica dbo.users, de Drupal). Ejecutar en la base
-- sufiatulado como paso de despliegue (no hay cadena Alembic en el proyecto).
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'user_lockout')
BEGIN
    CREATE TABLE dbo.user_lockout (
        clave NVARCHAR(120) NOT NULL PRIMARY KEY,
        conteo_fallos INT NOT NULL DEFAULT 0,
        bloqueada BIT NOT NULL DEFAULT 0,
        bloqueada_en_epoch FLOAT NOT NULL DEFAULT 0,
        expira_en_epoch FLOAT NOT NULL DEFAULT 0
    );
END;
