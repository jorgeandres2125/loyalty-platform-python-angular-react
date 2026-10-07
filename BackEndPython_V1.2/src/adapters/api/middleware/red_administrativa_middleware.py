from __future__ import annotations

import hmac
import ipaddress
import logging
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.shared.constants.eventos_seguridad import (
    LOGGER_SEGURIDAD,
    RESULTADO_EXITO,
    RESULTADO_FALLO,
)
from src.shared.constants.red_admin import (
    EVENTO_RED_ADMIN,
    HEADER_RED_ADMIN_EDGE_SECRET,
)

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)

RedGestion = ipaddress.IPv4Network | ipaddress.IPv6Network
DireccionIp = ipaddress.IPv4Address | ipaddress.IPv6Address


class RedAdministrativaMiddleware(BaseHTTPMiddleware):
    """AP-0052: restringe el acceso administrativo a segmentos de red de gestion.

    La restriccion primaria es de red (NSG, IP allow-list del edge, VPN, bastion,
    Private Endpoints). Este middleware es el control compensatorio de capa 7 que
    vive en la aplicacion: rechaza (fail-closed) toda peticion a rutas
    administrativas cuyo origen no pertenezca a los CIDRs de gestion autorizados,
    de modo que la restriccion queda versionada, auditada y demostrable aunque el
    perimetro fallara o no estuviera aun configurado.

    Confia en la IP reenviada por el edge SOLO si viene acompanada del secreto
    compartido (anti-suplantacion, mismo criterio que AP-0003 mTLS); en su defecto
    usa la IP de la conexion directa. Va por dentro de SecurityHeaders y de
    SecurityAudit y Contexto (su 403 recibe cabeceras y queda auditado y
    correlacionado) y por fuera de mTLS y del enrutamiento (rechaza antes de tocar
    la logica de negocio).
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        cidrs_gestion: tuple[str, ...],
        rutas_restringidas: tuple[str, ...],
        edge_secret: str,
        trusted_ip_header: str,
        enabled: bool,
    ) -> None:
        super().__init__(app)
        self._redes: tuple[RedGestion, ...] = self._parsear_cidrs(cidrs_gestion)
        self._rutas: tuple[str, ...] = rutas_restringidas
        self._edge_secret: str = edge_secret
        self._trusted_ip_header: str = trusted_ip_header
        self._enabled: bool = enabled

    @staticmethod
    def _parsear_cidrs(cidrs: tuple[str, ...]) -> tuple[RedGestion, ...]:
        redes: list[RedGestion] = []
        for cidr in cidrs:
            try:
                redes.append(ipaddress.ip_network(cidr, strict=False))
            except ValueError:
                _logger.warning("AP-0052: CIDR de gestion invalido, se ignora: %s", cidr)
        return tuple(redes)

    def _campos(
        self,
        resultado: str,
        severidad: SeveridadSeguridad,
        request: Request,
        ip: str | None,
    ) -> dict[str, object]:
        return {
            "evento_seguridad": EVENTO_RED_ADMIN,
            "severidad": severidad.value,
            "resultado": resultado,
            "actor": ip or "ip-desconocida",
            "recurso": request.url.path,
        }

    def _ip_cliente(self, request: Request) -> str | None:
        secreto: str = request.headers.get(HEADER_RED_ADMIN_EDGE_SECRET, "")
        if self._edge_secret and hmac.compare_digest(secreto, self._edge_secret):
            reenviada: str = request.headers.get(self._trusted_ip_header, "")
            if reenviada:
                # "cliente, proxy1, proxy2" -> el cliente original es el primero.
                return reenviada.split(",")[0].strip()
        if request.client is not None:
            return request.client.host
        return None

    def _en_red_gestion(self, ip_texto: str) -> bool:
        try:
            ip: DireccionIp = ipaddress.ip_address(ip_texto)
        except ValueError:
            return False
        return any(ip in red for red in self._redes)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if not self._enabled:
            return await call_next(request)
        ruta: str = request.url.path
        if not ruta.startswith(self._rutas):
            return await call_next(request)
        ip: str | None = self._ip_cliente(request)
        if ip is None or not self._en_red_gestion(ip):
            _logger.warning(
                "AP-0052: acceso administrativo desde red no autorizada, rechazado",
                extra=self._campos(RESULTADO_FALLO, SeveridadSeguridad.ALTA, request, ip),
            )
            return JSONResponse(
                status_code=403,
                content={"detail": "Acceso administrativo restringido a la red de gestion"},
            )
        _logger.info(
            "AP-0052: acceso administrativo desde red de gestion autorizada",
            extra=self._campos(RESULTADO_EXITO, SeveridadSeguridad.BAJA, request, ip),
        )
        return await call_next(request)
