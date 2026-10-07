from __future__ import annotations

from typing import Final

# AP-0025: hash de genesis para el primer eslabon de la cadena de sellos. 64 ceros hex
# (longitud de un digest SHA-256); centinela que no proviene de ningun evento real.
HASH_GENESIS: Final[str] = "0" * 64

# Prefijo del logger cuyos eventos se sellan (la cadena de auditoria de seguridad).
PREFIJO_LOGGER_SELLADO: Final[str] = "sufi.seguridad"

# Separador canonico para construir el contenido a hashear de cada evento.
SEPARADOR_CONTENIDO: Final[str] = "|"

# Nombres de los campos del sello que se adjuntan a cada LogRecord emitido.
CAMPO_SECUENCIA: Final[str] = "sello_secuencia"
CAMPO_HASH_PREVIO: Final[str] = "sello_hash_previo"
CAMPO_HASH_ACTUAL: Final[str] = "sello_hash"
CAMPO_HASH_CONTENIDO: Final[str] = "sello_hash_contenido"
CAMPO_CADENA_ID: Final[str] = "sello_cadena_id"
