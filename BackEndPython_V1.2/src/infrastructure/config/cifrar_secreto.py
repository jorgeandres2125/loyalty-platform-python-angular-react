"""AP-0092 -- utilidad de linea de comandos para cifrar credenciales del .env.

Uso (la KEK se toma de la variable de entorno SUFI_CONFIG_KEK, base64 de 32 bytes):

    python -m src.infrastructure.config.cifrar_secreto "mi-password-de-bd"

Imprime el valor `enc:gcm:...` listo para pegar en el archivo .env. Para generar
una KEK nueva:

    python -m src.infrastructure.config.cifrar_secreto --generar-kek
"""
from __future__ import annotations

import base64
import os
import secrets
import sys

from src.infrastructure.config.secret_decryptor import SecretDecryptor
from src.shared.constants.cifrado_config import ENV_CONFIG_KEK

_KEK_BYTES: int = 32


def _generar_kek() -> str:
    return base64.b64encode(secrets.token_bytes(_KEK_BYTES)).decode("ascii")


def _kek_actual() -> bytes | None:
    bruto: str = os.environ.get(ENV_CONFIG_KEK, "")
    if not bruto:
        return None
    return base64.b64decode(bruto)


def main(argumentos: list[str]) -> int:
    if not argumentos:
        print(__doc__)
        return 2
    if argumentos[0] == "--generar-kek":
        print(_generar_kek())
        return 0
    descifrador: SecretDecryptor = SecretDecryptor(_kek_actual())
    if not descifrador.kek_configurada:
        print(
            "ERROR: defina SUFI_CONFIG_KEK (base64 de 32 bytes) antes de cifrar. "
            "Genere una con: --generar-kek",
            file=sys.stderr,
        )
        return 1
    claro: str = argumentos[0]
    print(descifrador.cifrar_valor(claro))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
