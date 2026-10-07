"""Middleware CSRF double-submit (Medida A del plan de remediación, AP-0128).

Solo aplica cuando la petición se autentica por COOKIE: si el cliente usa
Authorization: Bearer (tests, integraciones máquina-a-máquina) no hay riesgo CSRF
y el middleware lo deja pasar. En métodos mutadores autenticados por cookie exige
que la cabecera X-CSRF-Token coincida con la cookie CSRF.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

_METODOS_SEGUROS: frozenset[str] = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        cookie_auth_name: str,
        csrf_cookie_name: str,
        csrf_header_name: str,
        enabled: bool = True,
    ) -> None:
        super().__init__(app)
        self._cookie_auth_name: str = cookie_auth_name
        self._csrf_cookie_name: str = csrf_cookie_name
        self._csrf_header_name: str = csrf_header_name
        self._enabled: bool = enabled

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if self._enabled and request.method not in _METODOS_SEGUROS:
            tiene_cookie_auth: bool = self._cookie_auth_name in request.cookies
            usa_bearer: bool = request.headers.get("Authorization", "").startswith("Bearer ")
            if tiene_cookie_auth and not usa_bearer:
                csrf_cookie: str | None = request.cookies.get(self._csrf_cookie_name)
                csrf_header: str | None = request.headers.get(self._csrf_header_name)
                if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "CSRF token inválido o ausente"},
                    )
        return await call_next(request)
