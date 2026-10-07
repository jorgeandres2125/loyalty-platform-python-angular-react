"""AP-0075 -- versionamiento del token SAPIN para converger a AES-256."""
from __future__ import annotations

from typing import Final

# Version moderna del token (la legacy v1 no lleva marcador: formato byte-a-byte del contrato
# con la plataforma externa MSP).
SAPIN_TOKEN_V2: Final[str] = "v2"

# Marcador que precede al token v2 (AES-256-GCM).
PREFIJO_TOKEN_V2: Final[str] = "v2."

# AES-256-GCM: clave de 32 bytes (256 bits), nonce de 12 bytes (estandar GCM).
LONGITUD_CLAVE_GCM_BYTES: Final[int] = 32
LONGITUD_NONCE_GCM_BYTES: Final[int] = 12

# Dato asociado autenticado que liga el criptograma a su proposito (AEAD).
AAD_TOKEN_SAPIN: Final[bytes] = b"sufi-sapin-token-v2"
