"""AP-0092 -- cifrado de credenciales en el archivo de configuracion.

Las credenciales de conexion (base de datos y otros sistemas) se almacenan
cifradas en los archivos .env con el marcador `enc:gcm:` seguido del blob
AES-256-GCM en base64. Una clave maestra (KEK), inyectada por entorno o Key
Vault, las descifra en memoria al arrancar. El texto plano nunca toca disco.
"""
from __future__ import annotations

from typing import Final

# Variable de entorno con la clave maestra (base64 de 32 bytes). Leida solo en
# settings.py (regla 15). Vacia = no hay credenciales cifradas (dev en plano).
ENV_CONFIG_KEK: Final[str] = "SUFI_CONFIG_KEK"

# Marcador que precede a un valor cifrado en el .env. Lo que sigue es el blob
# AES-256-GCM (ver, key_id, nonce, ct+tag) codificado en base64.
ENC_PREFIJO_CONFIG: Final[str] = "enc:gcm:"

# Dato asociado autenticado (AAD) que liga el criptograma a este proposito.
AAD_CONFIG_SECRETO: Final[str] = "sufi-config-secreto-v1"

# key_id fijo de la clave maestra activa dentro del registro del cifrador.
CONFIG_KEK_KEY_ID: Final[int] = 1

# Campos de Settings que pueden venir cifrados: credencial de conexion a la base
# de datos y credenciales o claves para acceder a otros sistemas.
CAMPOS_CREDENCIALES_CIFRABLES: Final[frozenset[str]] = frozenset(
    {
        "db_password",
        "jwt_secret_key",
        "smtp_password",
        "email_api_password",
        "sapin_aes_key_ctr",
        "sapin_aes_iv_ctr",
        "sapin_aes_key_cbc",
        "sapin_aes_key_gcm",
        "app_encryption_key",
        "app_encryption_keys_retired",
    }
)
