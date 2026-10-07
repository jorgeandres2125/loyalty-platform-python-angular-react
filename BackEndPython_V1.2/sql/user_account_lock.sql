-- AP-0157: tabla de estado de BLOQUEO DURO (administrativo/seguridad) de cuentas.
-- Propiedad del nuevo sistema (no modifica dbo.users, de Drupal). Independiente de
-- user_lockout (bloqueo suave, AP-0009): ambos pueden coexistir; el duro prevalece.
-- Ejecutar en la base sufiatulado como paso de despliegue (no hay cadena Alembic).
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'user_account_lock')
BEGIN
    CREATE TABLE dbo.user_account_lock (
        uid INT NOT NULL PRIMARY KEY,
        activo BIT NOT NULL DEFAULT 1,
        motivo NVARCHAR(400) NOT NULL DEFAULT '',
        bloqueado_en_epoch FLOAT NOT NULL DEFAULT 0,
        bloqueado_por_uid INT NOT NULL DEFAULT 0
    );
END;

-- AP-0157: motivo del bloqueo SUAVE administrativo (user_lockout, AP-0009). Columna
-- aditiva; el bloqueo automatico por intentos fallidos la deja vacia.
IF NOT EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.user_lockout') AND name = 'motivo'
)
BEGIN
    ALTER TABLE dbo.user_lockout ADD motivo NVARCHAR(400) NOT NULL DEFAULT '';
END;
