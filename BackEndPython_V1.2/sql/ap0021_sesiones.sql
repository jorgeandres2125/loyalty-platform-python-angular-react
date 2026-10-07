-- AP-0021: tablas de validacion de sesion (version de credencial y denylist de jti).
-- Propiedad del nuevo sistema (no modifican dbo.users, de Drupal). Ejecutar en la base
-- sufiatulado como paso de despliegue (no hay cadena Alembic en el proyecto).
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'user_token_version')
BEGIN
    CREATE TABLE dbo.user_token_version (
        uid INT NOT NULL PRIMARY KEY,
        token_version INT NOT NULL DEFAULT 1,
        updated_at DATETIME2 NULL
    );
END;

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'revoked_token')
BEGIN
    CREATE TABLE dbo.revoked_token (
        jti NVARCHAR(64) NOT NULL PRIMARY KEY,
        uid INT NOT NULL DEFAULT 0,
        expira_en_epoch FLOAT NOT NULL DEFAULT 0,
        motivo NVARCHAR(40) NOT NULL DEFAULT 'logout'
    );
END;
