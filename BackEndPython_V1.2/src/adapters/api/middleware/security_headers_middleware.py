"""Middleware de cabeceras de seguridad HTTP (Medida B del plan de remediación).

Emite HSTS sobre HTTPS (AP-0200) y un conjunto de cabeceras de endurecimiento:
X-Content-Type-Options (AP-0203), X-Frame-Options (AP-0201),
X-Permitted-Cross-Domain-Policies (AP-0205), Content-Security-Policy (AP-0204)
y Referrer-Policy. La CSP se relaja en /docs, /redoc y /openapi para no romper Swagger.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

_CSP_API: str = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
_CSP_DOCS: str = (
    "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net data:; "
    "img-src 'self' https://fastapi.tiangolo.com data:"
)
_RUTAS_DOCS: tuple[str, ...] = ("/docs", "/redoc", "/openapi")


# AP-0182: respuestas con datos dinamicos o sensibles no deben almacenarse en
# ninguna cache (navegador o proxy). no-store implica no-cache; se acompana de
# Pragma y Expires por compatibilidad con HTTP 1.0 e intermediarios antiguos.
_CACHE_NO_STORE: str = "no-store, no-cache, must-revalidate, max-age=0, private"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: ASGIApp, hsts_enabled: bool = True, hsts_max_age: int = 31536000
    ) -> None:
        super().__init__(app)
        self._hsts_enabled: bool = hsts_enabled
        self._hsts_max_age: int = hsts_max_age

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response: Response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Permitted-Cross-Domain-Policies", "none")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        # AP-0202 control heredado anti-XSS reflejado (complementa la CSP de AP-0204).
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
        ruta: str = request.url.path
        es_docs: bool = ruta.startswith(_RUTAS_DOCS)
        response.headers.setdefault("Content-Security-Policy", _CSP_DOCS if es_docs else _CSP_API)
        # AP-0182: no-store para todo lo que no sea documentacion publica estatica.
        if not es_docs:
            response.headers.setdefault("Cache-Control", _CACHE_NO_STORE)
            response.headers.setdefault("Pragma", "no-cache")
            response.headers.setdefault("Expires", "0")
        if self._hsts_enabled and request.url.scheme == "https":
            response.headers.setdefault(
                "Strict-Transport-Security",
                f"max-age={self._hsts_max_age}; includeSubDomains; preload",
            )
        return response
