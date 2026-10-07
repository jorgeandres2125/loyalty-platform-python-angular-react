"""Middleware de auditoría de seguridad (AP-0022).

Registra cada petición como evento de acceso (éxito/fallo según el status) y las
excepciones no controladas como evento excepcional. Marca las rutas que exponen
información confidencial y deriva el actor del JWT (cookie o bearer) best-effort.
"""
from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from src.domain.exceptions.token_invalido import TokenInvalido
from src.infrastructure.config.dependencies import (
    extraer_ip_cliente,
    get_security_audit_logger,
)
from src.infrastructure.config.settings import Settings
from src.infrastructure.logging.security_audit import SecurityAuditLogger
from src.infrastructure.security.jwt_handler import JWTHandler
from src.shared.constants.eventos_seguridad import RUTAS_CONFIDENCIALES

_RUTAS_IGNORADAS: tuple[str, ...] = ("/health", "/docs", "/redoc", "/openapi")


class SecurityAuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, settings: Settings) -> None:
        super().__init__(app)
        self._settings: Settings = settings
        self._jwt: JWTHandler = JWTHandler(settings.jwt_secret_key, settings.jwt_algorithm)
        self._audit: SecurityAuditLogger = get_security_audit_logger()

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
        ruta: str = request.url.path
        if request.method == "OPTIONS" or ruta.startswith(_RUTAS_IGNORADAS):
            return await call_next(request)

        inicio: float = time.perf_counter()
        ip: str = extraer_ip_cliente(request, self._settings)
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            self._audit.excepcional(
                ip=ip, recurso=ruta, detalle=f"{type(exc).__name__}: {exc}", exc=exc
            )
            raise

        duracion_ms: int = int((time.perf_counter() - inicio) * 1000)
        self._audit.acceso_http(
            metodo=request.method,
            ruta=ruta,
            status_code=response.status_code,
            ip=ip,
            actor=self._actor(request),
            duracion_ms=duracion_ms,
            confidencial=ruta.startswith(RUTAS_CONFIDENCIALES),
        )
        return response
