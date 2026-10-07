-- AP-0046, AP-0047 y AP-0048: credenciales temporales (DDL de referencia T-SQL).
-- Equivalente a la migracion Alembic 20260703_0012. No toca dbo.users (Drupal).
IF NOT EXISTS (
    SELECT 1 FROM sys.tables WHERE name = N'user_password_temporal'
)
BEGIN
    CREATE TABLE dbo.user_password_temporal (
        id                  INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_user_password_temporal PRIMARY KEY,
        uid                 INT            NOT NULL,
        hash_temporal       NVARCHAR(255)  NOT NULL,
        emitida_por_uid     INT            NOT NULL,
        emitida_por_usuario NVARCHAR(120)  NOT NULL,
        origen              NVARCHAR(20)   NOT NULL,
        motivo              NVARCHAR(200)  NULL,
        ip_emision          NVARCHAR(64)   NULL,
        emitida_iso         VARCHAR(40)    NOT NULL,
        expira_iso          VARCHAR(40)    NOT NULL,
        usada_iso           VARCHAR(40)    NULL,
        consumida_iso       VARCHAR(40)    NULL,
        estado              NVARCHAR(20)   NOT NULL
    );
    CREATE INDEX IX_user_password_temporal_uid_estado
        ON dbo.user_password_temporal (uid, estado);
END;
