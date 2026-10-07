"""Middleware de contexto de correlación por petición (AP-0024).

Establece en un ContextVar los campos de correlación — evento_id, usuario,
ip_local, ip_publica, metodo, ruta — antes de que el resto de la cadena de
middlewares y handlers ejecute. El ContextoSeguridadFilter los inyecta luego
en cada LogRecord, de modo que todo log emitido dentro de la petición queda
automáticamente correlacionado.
"""
from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from src.domain.exceptions.token_invalido import TokenInvalido
from src.infrastructure.config.dependencies import extraer_ip_cliente
from src.infrastructure.config.settings import Settings
from src.infrastructure.logging.contexto_seguridad import ContextoSeguridad
from src.infrastructure.security.jwt_handler import JWTHandler


class ContextoSeguridadMiddleware(BaseHTTPMiddleware):
    """Fija el contexto de correlación por petición (AP-0024)."""

    def __init__(self, app: ASGIApp, settings: Settings) -> None:
        super().__init__(app)
        self._settings: Settings = settings
        self._jwt: JWTHandler = JWTHandler(settings.jwt_secret_key, settings.jwt_algorithm)

    def _actor(self, request: Request) -> str:
        token: str | None = None
        autorizacion: str | None = request.headers.get("authorization")
        if autorizacion and autorizacion.lower().startswith("bearer "):
            token = autorizacion[7:]
        else:
            token = request.cookies.get(self._settings.cookie_auth_name)
        if not token:
            return "anonimo"
        try:
            payload: dict[str, object] = self._jwt.decode(token)
        except TokenInvalido:
            return "anonimo"
        return str(payload.get("sub", "anonimo"))

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        ip_local: str = request.client.host if request.client else "desconocida"
        ip_publica: str = extraer_ip_cliente(request, self._settings)
        ctx_token = ContextoSeguridad.establecer(
            {
                "evento_id": str(uuid.uuid4()),
                "usuario": self._actor(request),
                "ip_local": ip_local,
                "ip_publica": ip_publica,
                "metodo": request.method,
                "ruta": request.url.path,
            }
        )
        try:
            return await call_next(request)
        finally:
            ContextoSeguridad.limpiar(ctx_token)
