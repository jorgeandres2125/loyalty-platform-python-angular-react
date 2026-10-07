-- AP-0037: tabla lateral del reloj de vencimiento de contrasena (aviso a 7 dias).
-- Propiedad del nuevo sistema (no modifica dbo.users, de Drupal). Ejecutar en la
-- base sufiatulado como paso de despliegue (equivale a la migracion Alembic
-- 20260703_0010). El servicio es fail-safe: si la tabla no existe aun, el login y
-- el endpoint de sesion siguen funcionando y solo se omite el aviso.
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'user_password_expiracion')
BEGIN
    CREATE TABLE dbo.user_password_expiracion (
        uid INT NOT NULL PRIMARY KEY,
        password_cambiado_en DATETIME2 NOT NULL,
        updated_at DATETIME2 NULL
    );
END;
