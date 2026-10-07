from __future__ import annotations

import secrets

# AP-0179: generacion del Vector de Inicializacion (IV) para cifrado simetrico.
# El IV se calcula SIEMPRE en el momento de cifrar, con un CSPRNG (secrets), y su
# longitud es la del bloque del cifrado. Para AES el bloque es de 16 bytes (128
# bits) independientemente del tamano de clave; en AES-128 esa longitud coincide
# con la de la clave (IV == clave) y en AES-256 es la maxima longitud de IV valida
# que admite AES. Centralizar aqui la creacion del IV hace el control auditable
# (AP-0179): un unico punto donde nacen los IV, nunca fijos ni reutilizados.


def generar_iv(longitud: int) -> bytes:
    """Devuelve un IV aleatorio recien generado de `longitud` bytes (CSPRNG)."""
    if longitud <= 0:
        raise ValueError("la longitud del IV debe ser un entero positivo")
    return secrets.token_bytes(longitud)
