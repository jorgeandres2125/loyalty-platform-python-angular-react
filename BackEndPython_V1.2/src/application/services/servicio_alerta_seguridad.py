from __future__ import annotations

import logging
import time
from collections.abc import Callable, Sequence

from src.domain.entities.alerta_seguridad import AlertaSeguridad
from src.domain.ports.outbound.notificador_evento_seguridad import (
    NotificadorEventoSeguridad,
)
from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.shared.constants.alertas import (
    EVENTO_ALERTA_EMITIDA,
    EVENTO_ALERTA_NO_ENTREGADA,
    RANGO_SEVERIDAD,
)
from src.shared.constants.eventos_seguridad import LOGGER_SEGURIDAD

_logger: logging.Logger = logging.getLogger(LOGGER_SEGURIDAD)
_MAX_VISTOS: int = 2048


class ServicioAlertaSeguridad:
    """AP-0134: evalua cada evento de seguridad y, si su severidad alcanza el umbral,
    despacha una alerta a los canales configurados. Es fail-safe (nunca interrumpe la
    peticion), asincrono (no bloquea) y con deduplicacion por ventana para evitar
    tormentas de alertas. Control compensatorio del pipeline SIEM: funciona sin el."""

    def __init__(
        self,
        notificadores: Sequence[NotificadorEventoSeguridad],
        umbral: SeveridadSeguridad,
        habilitado: bool,
        dedup_ventana_seg: int,
        reloj: Callable[[], float] | None = None,
    ) -> None:
        self._notificadores: Sequence[NotificadorEventoSeguridad] = notificadores
        self._umbral_rango: int = RANGO_SEVERIDAD[umbral]
        self._habilitado: bool = habilitado
        self._ventana: float = float(dedup_ventana_seg)
        self._reloj: Callable[[], float] = reloj or time.monotonic
        self._vistos: dict[str, float] = {}

    def debe_alertar(self, alerta: AlertaSeguridad) -> bool:
        if not self._habilitado:
            return False
        if RANGO_SEVERIDAD[alerta.severidad] < self._umbral_rango:
            return False
        ahora: float = self._reloj()
        ultimo: float | None = self._vistos.get(alerta.clave_dedup)
        if ultimo is not None and (ahora - ultimo) < self._ventana:
            return False
        self._registrar_visto(alerta.clave_dedup, ahora)
        return True

    def _registrar_visto(self, clave: str, ahora: float) -> None:
        if len(self._vistos) >= _MAX_VISTOS:
            self._vistos = {
                clave_v: momento_v
                for clave_v, momento_v in self._vistos.items()
                if (ahora - momento_v) < self._ventana
            }
        self._vistos[clave] = ahora

    async def despachar(self, alerta: AlertaSeguridad) -> None:
        entregada: bool = False
        for notificador in self._notificadores:
            try:
                await notificador.alertar(alerta)
                entregada = True
            except Exception:
                _logger.warning(
                    "AP-0134 alerta no entregada",
                    extra={
                        "evento_seguridad": EVENTO_ALERTA_NO_ENTREGADA,
                        "severidad": SeveridadSeguridad.MEDIA.value,
                        "resultado": "fallo",
                        "actor": alerta.actor,
                        "canal": type(notificador).__name__,
                    },
                )
        _logger.info(
            "AP-0134 alerta emitida",
            extra={
                "evento_seguridad": EVENTO_ALERTA_EMITIDA,
                "severidad": SeveridadSeguridad.INFORMATIVA.value,
                "resultado": "exito" if entregada else "fallo",
                "actor": alerta.actor,
                "alerta_evento": alerta.evento,
                "alerta_severidad": alerta.severidad.value,
                "correlation_id": alerta.correlation_id,
            },
        )

    def procesar(self, alerta: AlertaSeguridad) -> None:
        # Punto de entrada sincrono (desde el AlertaHandler). Aplica el gating y, si
        # procede, agenda el despacho en el event loop sin bloquear la peticion. Sin loop
        # en curso (arranque o contexto sincrono) no se despacha async: el evento ya quedo
        # en el log, que es la fuente de verdad.
        if not self.debe_alertar(alerta):
            return
        try:
            import asyncio

            loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        except RuntimeError:
            return
        loop.create_task(self.despachar(alerta))
