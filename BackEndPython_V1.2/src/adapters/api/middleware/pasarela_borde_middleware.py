from __future__ import annotations

import hmac
import logging
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD, RESULTADO_FALLO
from src.shared.constants.pasarela_borde import EVENTO_PASARELA_BORDE

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)


class PasarelaBordeMiddleware(BaseHTTPMiddleware):
    """AP-0064: control compensatorio de capa 7. La app solo debe consumirse a traves del
    intermediario seguro (WAF, proxy reverso o API gateway). Fail-closed: rechaza (403) toda
    peticion que no acredite haber atravesado el borde, comprobando en tiempo constante la
    cabecera de borde que el intermediario inyecta. Es conmutable (enabled) para no romper dev
    ni el arranque antes de que el edge exista, y exime rutas internas de salud (sondas del
    balanceador). Va por dentro de SecurityHeaders y de la auditoria (su 403 recibe cabeceras y
    queda auditado y correlacionado) y por fuera del enrutamiento (rechaza antes de la logica de
    negocio), mismo criterio que AP-0052 y AP-0003.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        edge_secret: str,
        header: str,
        rutas_exentas: tuple[str, ...],
        enabled: bool,
    ) -> None:
        super().__init__(app)
        self._edge_secret: str = edge_secret
        self._header: str = header
        self._rutas_exentas: tuple[str, ...] = rutas_exentas
        self._enabled: bool = enabled

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if not self._enabled:
            return await call_next(request)
        ruta: str = request.url.path
        if ruta.startswith(self._rutas_exentas):
            return await call_next(request)
        recibido: str = request.headers.get(self._header, "")
        if self._edge_secret and hmac.compare_digest(recibido, self._edge_secret):
            return await call_next(request)
        _logger.warning(
            "AP-0064: peticion sin acreditacion de borde, rechazada (posible bypass del borde)",
            extra={
                "evento_seguridad": EVENTO_PASARELA_BORDE,
                "severidad": SeveridadSeguridad.ALTA.value,
                "resultado": RESULTADO_FALLO,
                "recurso": ruta,
            },
        )
        return JSONResponse(
            status_code=403,
            content={"detail": "Acceso permitido solo a traves del intermediario seguro"},
        )
