from __future__ import annotations

from typing import Final

# AP-0185: metodos HTTP minimos que la aplicacion soporta. Todo metodo fuera de
# este conjunto (TRACE, CONNECT, TRACK, etc.) se rechaza con 405 en el borde.
METODOS_HTTP_PERMITIDOS: Final[frozenset[str]] = frozenset(
    {"GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"}
)
# Valor de la cabecera Allow en la respuesta 405 (orden estable).
METODOS_HTTP_ALLOW: Final[str] = "GET, HEAD, OPTIONS, POST, PUT, PATCH, DELETE"
