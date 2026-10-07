from __future__ import annotations

import logging
from typing import Final

from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.shared.constants.eventos_seguridad import (
    EVENTO_ACCESO,
    EVENTO_ACCESO_CONFIDENCIAL,
    EVENTO_AUTENTICACION,
    EVENTO_AUTORIZACION,
    EVENTO_CAMBIO_CREDENCIAL,
    EVENTO_EXCEPCIONAL,
    LOGGER_SEGURIDAD,
    RESULTADO_EXITO,
    RESULTADO_FALLO,
)

# Mapeo severidad de seguridad → nivel de logging estándar (AP-0023).
_NIVEL_POR_SEVERIDAD: Final[dict[SeveridadSeguridad, int]] = {
    SeveridadSeguridad.INFORMATIVA: logging.INFO,
    SeveridadSeguridad.BAJA: logging.INFO,
    SeveridadSeguridad.MEDIA: logging.WARNING,
    SeveridadSeguridad.ALTA: logging.ERROR,
    SeveridadSeguridad.CRITICA: logging.CRITICAL,
}


class SecurityAuditLogger:
    """Registro estructurado de eventos de seguridad (AP-0022 / AP-0023).

    Emite a un logger dedicado (`sufi.seguridad`); los campos viajan en `extra` y el
    `JSONFormatter` los anida bajo "extra". Cada evento lleva una `severidad` de
    seguridad explícita (AP-0023) además del `level` del logger, derivado de ella.
    """

    def __init__(self) -> None:
        self._logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)

    def _registrar(
        self,
        *,
        severidad: SeveridadSeguridad,
        mensaje: str,
        evento: str,
        resultado: str,
        actor: str,
        ip: str,
        recurso: str | None = None,
        detalle: str | None = None,
        confidencial: bool = False,
        extra: dict[str, object] | None = None,
        exc: BaseException | None = None,
    ) -> None:
        campos: dict[str, object] = {
            "evento_seguridad": evento,
            "severidad": severidad.value,
            "resultado": resultado,
            "actor": actor,
            "ip": ip,
            "recurso": recurso,
            "detalle": detalle,
            "confidencial": confidencial,
        }
        if extra:
            campos.update(extra)
        self._logger.log(_NIVEL_POR_SEVERIDAD[severidad], mensaje, extra=campos, exc_info=exc)

    # ── Autenticación ────────────────────────────────────────────────────────
    def autenticacion(
        self, *, exito: bool, actor: str, ip: str, detalle: str | None = None
    ) -> None:
        self._registrar(
            severidad=SeveridadSeguridad.INFORMATIVA if exito else SeveridadSeguridad.MEDIA,
            mensaje=f"autenticacion:{'exito' if exito else 'fallo'} actor={actor}",
            evento=EVENTO_AUTENTICACION,
            resultado=RESULTADO_EXITO if exito else RESULTADO_FALLO,
            actor=actor,
            ip=ip,
            detalle=detalle,
        )

    # ── Cambio de credencial (AP-0020) ───────────────────────────────────────
    def cambio_credencial(
        self, *, exito: bool, actor: str, ip: str, detalle: str | None = None
    ) -> None:
        self._registrar(
            severidad=SeveridadSeguridad.BAJA if exito else SeveridadSeguridad.MEDIA,
            mensaje=f"cambio_credencial:{'exito' if exito else 'fallo'} actor={actor}",
            evento=EVENTO_CAMBIO_CREDENCIAL,
            resultado=RESULTADO_EXITO if exito else RESULTADO_FALLO,
            actor=actor,
            ip=ip,
            detalle=detalle,
        )

    # ── Acceso HTTP (middleware) ──────────────────────────────────────────────
    # -- Cambio de autorización (AP-0054 / AP-0022) --
    def cambio_autorizacion(
        self,
        *,
        exito: bool,
        actor: str,
        ip: str,
        recurso: str,
        detalle: str | None = None,
    ) -> None:
        """Registra un cambio de autorización: asignación de roles a usuarios o
        cambios en la matriz de permisos rol-módulo. Marcado como confidencial."""
        self._registrar(
            severidad=SeveridadSeguridad.BAJA if exito else SeveridadSeguridad.MEDIA,
            mensaje=f"cambio_autorizacion:{'exito' if exito else 'fallo'} recurso={recurso}",
            evento=EVENTO_AUTORIZACION,
            resultado=RESULTADO_EXITO if exito else RESULTADO_FALLO,
            actor=actor,
            ip=ip,
            recurso=recurso,
            detalle=detalle,
            confidencial=True,
        )
    def acceso_http(
        self,
        *,
        metodo: str,
        ruta: str,
        status_code: int,
        ip: str,
        actor: str,
        duracion_ms: int,
        confidencial: bool,
    ) -> None:
        if status_code >= 500:
            severidad: SeveridadSeguridad = SeveridadSeguridad.ALTA
        elif status_code >= 400:
            severidad = SeveridadSeguridad.MEDIA
        elif confidencial:
            severidad = SeveridadSeguridad.BAJA
        else:
            severidad = SeveridadSeguridad.INFORMATIVA
        self._registrar(
            severidad=severidad,
            mensaje=f"{metodo} {ruta} -> {status_code}",
            evento=EVENTO_ACCESO_CONFIDENCIAL if confidencial else EVENTO_ACCESO,
            resultado=RESULTADO_EXITO if status_code < 400 else RESULTADO_FALLO,
            actor=actor,
            ip=ip,
            recurso=ruta,
            confidencial=confidencial,
            extra={"metodo": metodo, "status_code": status_code, "duracion_ms": duracion_ms},
        )

    # ── Evento excepcional (excepción no controlada) ──────────────────────────
    def excepcional(
        self, *, ip: str, recurso: str, detalle: str, exc: BaseException | None = None
    ) -> None:
        self._registrar(
            severidad=SeveridadSeguridad.ALTA,
            mensaje=f"excepcion no controlada en {recurso}",
            evento=EVENTO_EXCEPCIONAL,
            resultado=RESULTADO_FALLO,
            actor="desconocido",
            ip=ip,
            recurso=recurso,
            detalle=detalle,
            exc=exc,
        )
