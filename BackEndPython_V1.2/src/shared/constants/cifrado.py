from __future__ import annotations

from typing import Final

# Catálogo de campos restringidos cifrados a nivel de aplicación (AP-0147 / AP-0095).
# tabla -> columnas (lógicas, en claro) que se persisten cifradas en una columna
# hermana <columna>_enc VARBINARY(MAX). El backfill y los repositorios leen este
# catálogo para saber qué cifrar/descifrar. Se amplía por configuración, no por
# código nuevo.
TABLA_PERFIL_CONTACTO: Final[str] = "users_perfil_contacto"

SUFIJO_CIFRADO: Final[str] = "_enc"

CAMPOS_RESTRINGIDOS: Final[dict[str, tuple[str, ...]]] = {
    TABLA_PERFIL_CONTACTO: (
        "numero_de_cuenta",
        "tipo_de_cuenta",
        "direccion",
        "telefono",
        "celular",
        "email",
    ),
}

# AP-0179: tamano del bloque AES en bytes (128 bits). Es la longitud del IV para
# AES-CBC/CTR, igual a la longitud de clave en AES-128 y la maxima valida en AES-256.
TAMANO_BLOQUE_AES_BYTES: Final[int] = 16
