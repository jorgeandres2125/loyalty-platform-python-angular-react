from __future__ import annotations

from typing import Final

# Política de longitud mínima de contraseña (AP-0044).
#
# La política se aplica al ESTABLECER/CAMBIAR la contraseña, nunca al autenticar:
# subir el mínimo en el login bloquearía a usuarios legacy cuyo hash corresponde a
# una clave más corta. El control distingue dos poblaciones:
#
#   • Usuario final (humano): mínimo 12 caracteres.
#   • Usuario de servicio / conexión entre sistemas: mínimo 20 caracteres.
#
# Los validadores que consumen estas constantes:
#   - CambioPasswordRequest  → PASSWORD_MIN_LONGITUD_USUARIO_FINAL
#   - Settings (staging/prod) → PASSWORD_MIN_LONGITUD_USUARIO_SERVICIO
PASSWORD_MIN_LONGITUD_USUARIO_FINAL: Final[int] = 12

PASSWORD_MIN_LONGITUD_USUARIO_SERVICIO: Final[int] = 20

# Complejidad de contraseña (AP-0051): mínimo 3 de los 4 tipos de carácter
# (minúscula, mayúscula, dígito, carácter especial). Se exige al ESTABLECER la
# clave, con el mismo criterio que la longitud (no aplica al autenticar).
PASSWORD_MIN_TIPOS_CARACTER: Final[int] = 3


def contar_tipos_caracter(password: str) -> int:
    """Cuenta cuántos de los 4 tipos de carácter aparecen en la contraseña (AP-0051).

    Tipos: minúscula, mayúscula, dígito y especial (cualquier carácter no
    alfanumérico). Función pura, sin dependencias de framework, para poder
    reutilizarla desde el validador del esquema y desde los tests.
    """
    tiene_minuscula: bool = any(c.islower() for c in password)
    tiene_mayuscula: bool = any(c.isupper() for c in password)
    tiene_digito: bool = any(c.isdigit() for c in password)
    tiene_especial: bool = any(not c.isalnum() for c in password)
    return sum((tiene_minuscula, tiene_mayuscula, tiene_digito, tiene_especial))
