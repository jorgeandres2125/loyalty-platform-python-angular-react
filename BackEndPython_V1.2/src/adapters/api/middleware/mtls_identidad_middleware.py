from __future__ import annotations

import hmac
import logging
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from src.domain.ports.outbound.registro_certificados_cliente import (
    RegistroCertificadosCliente,
)
from src.domain.value_objects.identidad_certificado import IdentidadCertificado
from src.domain.value_objects.principal_certificado import PrincipalCertificado
from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.shared.constants.eventos_seguridad import (
    LOGGER_SEGURIDAD,
    RESULTADO_EXITO,
    RESULTADO_FALLO,
)
from src.shared.constants.mtls import (
    EVENTO_MTLS,
    HEADER_CLIENT_CERT_FINGERPRINT,
    HEADER_CLIENT_CERT_SERIAL,
    HEADER_CLIENT_CERT_SUBJECT,
    HEADER_MTLS_EDGE_SECRET,
)

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)


class MtlsIdentidadMiddleware(BaseHTTPMiddleware):
    """AP-0003: exige y valida el certificado de cliente (mTLS) en rutas criticas.

    El edge (Ingress o API Gateway) termina y valida el certificado de cliente en el
    handshake mTLS y propaga la identidad X.509 en cabeceras de confianza junto a un
    secreto compartido. Este middleware:

    1. Verifica el secreto del edge (anti-suplantacion) antes de confiar en las
       cabeceras de identidad.
    2. Construye la IdentidadCertificado y la mapea a un PrincipalCertificado via la
       allow-list (puerto RegistroCertificadosCliente).
    3. En las rutas obligatorias, rechaza con 403 cualquier peticion sin certificado
       valido, autorizado y activo (fail-closed).
    4. Adjunta el principal a request.state y audita el resultado (AP-0022).

    En las rutas no obligatorias no bloquea: si hay certificado valido enriquece el
    contexto, y si no, deja pasar (los controles de capa 7 siguen aplicando).
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        registro: RegistroCertificadosCliente,
        rutas_obligatorias: tuple[str, ...],
        edge_secret: str,
        enabled: bool,
    ) -> None:
        super().__init__(app)
        self._registro: RegistroCertificadosCliente = registro
        self._rutas_obligatorias: tuple[str, ...] = rutas_obligatorias
        self._edge_secret: str = edge_secret
        self._enabled: bool = enabled

    def _campos(
        self,
        resultado: str,
        severidad: SeveridadSeguridad,
        request: Request,
        principal: PrincipalCertificado | None,
    ) -> dict[str, object]:
        return {
            "evento_seguridad": EVENTO_MTLS,
            "severidad": severidad.value,
            "resultado": resultado,
            "actor": principal.sistema if principal else "cert-desconocido",
            "recurso": request.url.path,
        }

    def _identidad_confiable(self, request: Request) -> IdentidadCertificado | None:
        fingerprint: str | None = request.headers.get(HEADER_CLIENT_CERT_FINGERPRINT)
        if not fingerprint:
            return None
        secreto: str = request.headers.get(HEADER_MTLS_EDGE_SECRET, "")
        if not self._edge_secret or not hmac.compare_digest(secreto, self._edge_secret):
            _logger.warning(
                "mTLS: cabeceras de certificado sin secreto de edge valido; se ignoran",
                extra=self._campos(RESULTADO_FALLO, SeveridadSeguridad.ALTA, request, None),
            )
            return None
        return IdentidadCertificado(
            fingerprint=fingerprint,
            subject=request.headers.get(HEADER_CLIENT_CERT_SUBJECT, ""),
            serial=request.headers.get(HEADER_CLIENT_CERT_SERIAL, ""),
        )

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if not self._enabled:
            return await call_next(request)

        ruta: str = request.url.path
        obligatorio: bool = ruta.startswith(self._rutas_obligatorias)
        identidad: IdentidadCertificado | None = self._identidad_confiable(request)
        principal: PrincipalCertificado | None = None
        if identidad is not None:
            resuelto: PrincipalCertificado | None = self._registro.resolver(identidad)
            if resuelto is not None and resuelto.activo:
                principal = resuelto
                request.state.principal_certificado = principal

        if obligatorio and principal is None:
            _logger.warning(
                "mTLS obligatorio: certificado de cliente ausente o no autorizado",
                extra=self._campos(RESULTADO_FALLO, SeveridadSeguridad.ALTA, request, None),
            )
            return JSONResponse(
                status_code=403,
                content={"detail": "Se requiere un certificado de cliente valido"},
            )

        if principal is not None:
            _logger.info(
                "mTLS: certificado de cliente autenticado",
                extra=self._campos(RESULTADO_EXITO, SeveridadSeguridad.BAJA, request, principal),
            )
        return await call_next(request)
