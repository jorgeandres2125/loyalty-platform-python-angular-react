from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD
from src.shared.constants.parametros_http import PARAMETROS_QUERY_MULTIVALOR
from src.shared.utils.parametros_duplicados import colapsar_parametros_duplicados

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)


class ParametrosDuplicadosMiddleware(BaseHTTPMiddleware):
    """AP-0199: descarta parametros de query repetidos no definidos como
    multi-valor.

    Ante HTTP Parameter Pollution (por ejemplo el mismo nombre dos veces en el
    query), la app no debe quedar a merced de que un componente aguas abajo elija
    una u otra ocurrencia: para cada nombre no declarado multi-valor se
    conserva SOLO la primera aparicion y se descartan las demas, normalizando el
    query_string del scope ASGI antes del enrutamiento y la validacion. El descarte
    se audita en el logger de seguridad.
    """

    def __init__(
        self,
        app: ASGIApp,
        nombres_multivalor: frozenset[str] = PARAMETROS_QUERY_MULTIVALOR,
    ) -> None:
        super().__init__(app)
        self._nombres_multivalor: frozenset[str] = nombres_multivalor

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        query_string: bytes = request.scope.get("query_string", b"")
        if query_string:
            normalizado, duplicados = colapsar_parametros_duplicados(
                query_string, self._nombres_multivalor
            )
            if duplicados:
                request.scope["query_string"] = normalizado
                _logger.warning(
                    "Parametros de query duplicados descartados (HPP): %s",
                    ", ".join(duplicados),
                )
        return await call_next(request)
