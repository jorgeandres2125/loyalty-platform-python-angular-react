from __future__ import annotations

import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from src.domain.exceptions.acceso_no_autorizado import AccesoNoAutorizado
from src.domain.exceptions.audiencia_no_permitida import AudienciaNoPermitida
from src.domain.exceptions.email_invalido import EmailInvalido
from src.domain.exceptions.email_no_unico import EmailNoUnico
from src.domain.exceptions.paso_omitido import PasoOmitido
from src.domain.exceptions.password_insegura import PasswordInsegura


async def rate_limit_excedido_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    _logger.warning(
        "rate_limit_excedido",
        extra={
            "ip": request.client.host if request.client else "desconocido",
            "ruta": request.url.path,
            "limite": str(exc.detail),
        },
    )
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiadas solicitudes. Intente mas tarde."},
    )


_logger: logging.Logger = logging.getLogger("sufi.api")

_MSG_ERROR_INTERNO: str = "Error interno del servidor."


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """AP-0119: ninguna excepcion no controlada revela stack trace, SQL ni nombres
    de tablas o base de datos al cliente."""
    _logger.exception(
        "error_no_controlado",
        extra={"ruta": request.url.path, "metodo": request.method},
    )
    return JSONResponse(status_code=500, content={"detail": _MSG_ERROR_INTERNO})


async def email_invalido_handler(request: Request, exc: EmailInvalido) -> JSONResponse:
    """AP-0141: formato de correo invalido (RFC822) -> 400."""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def email_no_unico_handler(request: Request, exc: EmailNoUnico) -> JSONResponse:
    """AP-0141: correo ya registrado (no unico) -> 409."""
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def audiencia_no_permitida_handler(
    request: Request, exc: AudienciaNoPermitida
) -> JSONResponse:
    """AP-0146: aplicacion de terceros no autorizada -> 400."""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def password_insegura_handler(
    request: Request, exc: PasswordInsegura
) -> JSONResponse:
    """AP-0159: contrasena rechazada por blacklist o datos contextuales -> 400."""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def paso_omitido_handler(request: Request, exc: PasoOmitido) -> JSONResponse:
    """AP-0187: intento de saltar un paso del wizard -> 409 Conflict."""
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def acceso_no_autorizado_handler(
    request: Request, exc: AccesoNoAutorizado
) -> JSONResponse:
    """AP-0053: el actor intento operar sobre un recurso ajeno -> 403 Forbidden."""
    return JSONResponse(status_code=403, content={"detail": str(exc)})
