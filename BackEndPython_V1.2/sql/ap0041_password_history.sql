-- AP-0041: historial de contrasenas por usuario (no reutilizar las ultimas 24).
-- Propiedad del nuevo sistema (no modifica dbo.users, de Drupal). Ejecutar en la base
-- sufiatulado como paso de despliegue (equivale a la migracion Alembic 20260703_0011).
-- Guarda hashes (nunca texto plano); se poda a 24 filas por usuario en cada cambio.
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'user_password_history')
BEGIN
    CREATE TABLE dbo.user_password_history (
        id            INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        uid           INT           NOT NULL,
        password_hash NVARCHAR(255) NOT NULL,
        creado_iso    NVARCHAR(40)  NOT NULL
    );
    CREATE INDEX IX_user_password_history_uid_fecha
        ON dbo.user_password_history (uid, creado_iso DESC);
END;
