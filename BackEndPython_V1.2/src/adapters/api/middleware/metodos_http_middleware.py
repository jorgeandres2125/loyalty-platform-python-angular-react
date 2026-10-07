from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.shared.constants.http_methods import (
    METODOS_HTTP_ALLOW,
    METODOS_HTTP_PERMITIDOS,
)


class MetodosHttpMiddleware(BaseHTTPMiddleware):
    """AP-0185: solo admite los metodos HTTP minimos requeridos.

    Cualquier metodo fuera de METODOS_HTTP_PERMITIDOS (TRACE, CONNECT, TRACK, etc.)
    se rechaza con 405 Method Not Allowed y cabecera Allow, en el borde de la app y
    sin llegar al enrutador. Mitiga Cross-Site Tracing (XST) y reduce la superficie.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.method not in METODOS_HTTP_PERMITIDOS:
            return JSONResponse(
                status_code=405,
                content={"detail": "Metodo HTTP no permitido"},
                headers={"Allow": METODOS_HTTP_ALLOW},
            )
        return await call_next(request)
