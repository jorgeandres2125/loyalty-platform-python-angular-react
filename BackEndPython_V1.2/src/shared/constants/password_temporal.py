from __future__ import annotations

from typing import Final

# AP-0046, AP-0047 y AP-0048: contrasenas temporales.
#
# AP-0048: la vigencia maxima es de 120 minutos y ese techo es NORMATIVO: Settings
# lo refuerza con un validador (le=PASSWORD_TEMPORAL_TTL_MINUTOS_MAXIMO) para que
# ningun entorno pueda configurar un TTL mayor. El TTL es una duracion, no una
# fecha calendario: toda la aritmetica es UTC.
PASSWORD_TEMPORAL_TTL_MINUTOS_DEFECTO: Final[int] = 120
PASSWORD_TEMPORAL_TTL_MINUTOS_MAXIMO: Final[int] = 120

# Longitud de la clave temporal generada. El minimo del rango (12) cumple AP-0044
# por construccion; el defecto (16) da margen adicional de entropia.
PASSWORD_TEMPORAL_LONGITUD_DEFECTO: Final[int] = 16

# Alfabeto legible para claves que se dictan o transcriben: excluye caracteres
# ambiguos (cero, o mayuscula, uno, ele minuscula, i mayuscula). El generador
# garantiza presencia de las tres clases (AP-0051: al menos 3 de 4 tipos).
PASSWORD_TEMPORAL_MINUSCULAS: Final[str] = "abcdefghjkmnpqrstuvwxyz"
PASSWORD_TEMPORAL_MAYUSCULAS: Final[str] = "ABCDEFGHJKMNPQRSTUVWXYZ"
PASSWORD_TEMPORAL_DIGITOS: Final[str] = "23456789"
