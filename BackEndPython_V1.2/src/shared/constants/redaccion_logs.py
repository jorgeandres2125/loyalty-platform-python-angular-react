from __future__ import annotations

from typing import Final

# AP-0087: marcador con el que se reemplaza cualquier valor sensible en los logs.
REDACTADO: Final[str] = "[REDACTED]"

# Nombres de campo (en minuscula) cuyo valor nunca debe quedar en claro en los
# logs tecnicos ni en los registros de auditoria. Se comparan contra las claves
# de los campos 'extra' y de los dicts anidados. El identificador de usuario y la
# IP no se incluyen: son necesarios para la trazabilidad de auditoria (AP-0022/24).
CLAVES_SENSIBLES: Final[frozenset[str]] = frozenset(
    {
        "password",
        "contrasena",
        "nueva_password",
        "password_actual",
        "confirmar_password",
        "pwd",
        "passwd",
        "secret",
        "secret_key",
        "jwt_secret_key",
        "db_password",
        "smtp_password",
        "email_api_password",
        "app_encryption_key",
        "app_encryption_keys_retired",
        "sapin_aes_key_ctr",
        "sapin_aes_iv_ctr",
        "sapin_aes_key_cbc",
        "sapin_aes_key_gcm",
        "token",
        "access_token",
        "refresh_token",
        "jwt",
        "authorization",
        "cookie",
        "set-cookie",
        "csrf",
        "csrf_token",
        "api_key",
        "apikey",
        "otp",
        "codigo_verificacion",
        "numero_de_cuenta",
        "numero_cuenta",
        "cuenta_bancaria",
    }
)
