"""AP-0134: alertamiento de eventos de seguridad sensibles. Prueba el gating por umbral,
la deduplicacion, el fail-safe (un canal caido no rompe el resto), que el handler deriva
la alerta del registro y no re-alerta sus propios eventos, y los adaptadores."""
from __future__ import annotations

import logging

from src.application.services.servicio_alerta_seguridad import ServicioAlertaSeguridad
from src.domain.entities.alerta_seguridad import AlertaSeguridad
from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad
from src.infrastructure.external.notificador_correo_alerta import NotificadorCorreoAlerta
from src.infrastructure.external.notificador_webhook import NotificadorWebhook
from src.infrastructure.logging.alerta_handler import AlertaHandler, alerta_desde_record


class _Capturador:
    def __init__(self) -> None:
        self.recibidas: list[AlertaSeguridad] = []

    async def alertar(self, alerta: AlertaSeguridad) -> None:
        self.recibidas.append(alerta)


class _CanalCaido:
    async def alertar(self, alerta: AlertaSeguridad) -> None:
        raise RuntimeError("canal de alerta caido")


class _RelojFake:
    def __init__(self, valor: float) -> None:
        self.valor: float = valor

    def ahora(self) -> float:
        return self.valor


class _CorreoFake:
    def __init__(self) -> None:
        self.enviados: list[tuple[str, str]] = []

    async def enviar_async(
        self, destinatario: str, asunto: str, cuerpo_texto: str, cuerpo_html: str
    ) -> None:
        self.enviados.append((destinatario, asunto))


def _alerta(sev: SeveridadSeguridad, evento: str = "autenticacion") -> AlertaSeguridad:
    return AlertaSeguridad(
        titulo="t",
        severidad=sev,
        evento=evento,
        resultado="fallo",
        actor="jperez",
        ip="203.0.113.9",
        correlation_id="req-1",
    )


def _servicio(
    notificadores: list[object],
    umbral: SeveridadSeguridad = SeveridadSeguridad.ALTA,
    habilitado: bool = True,
    ventana: int = 60,
    reloj: object | None = None,
) -> ServicioAlertaSeguridad:
    return ServicioAlertaSeguridad(
        notificadores=notificadores,  # type: ignore[arg-type]
        umbral=umbral,
        habilitado=habilitado,
        dedup_ventana_seg=ventana,
        reloj=reloj,  # type: ignore[arg-type]
    )


def test_debe_alertar_por_umbral() -> None:
    # Eventos distintos para que la deduplicacion (por evento+actor+ip) no interfiera.
    svc = _servicio([_Capturador()])
    assert svc.debe_alertar(_alerta(SeveridadSeguridad.BAJA, "e_baja")) is False
    assert svc.debe_alertar(_alerta(SeveridadSeguridad.MEDIA, "e_media")) is False
    assert svc.debe_alertar(_alerta(SeveridadSeguridad.ALTA, "e_alta")) is True
    assert svc.debe_alertar(_alerta(SeveridadSeguridad.CRITICA, "e_critica")) is True


def test_deshabilitado_no_alerta() -> None:
    svc = _servicio([_Capturador()], habilitado=False)
    assert svc.debe_alertar(_alerta(SeveridadSeguridad.CRITICA)) is False


def test_dedup_suprime_repeticion_en_ventana() -> None:
    reloj = _RelojFake(100.0)
    svc = _servicio([_Capturador()], ventana=60, reloj=reloj.ahora)
    alerta = _alerta(SeveridadSeguridad.ALTA)
    assert svc.debe_alertar(alerta) is True
    assert svc.debe_alertar(alerta) is False
    reloj.valor = 161.0
    assert svc.debe_alertar(alerta) is True


async def test_despachar_entrega_a_todos_los_canales() -> None:
    a, b = _Capturador(), _Capturador()
    svc = _servicio([a, b])
    await svc.despachar(_alerta(SeveridadSeguridad.ALTA))
    assert len(a.recibidas) == 1
    assert len(b.recibidas) == 1


async def test_despachar_fail_safe_un_canal_caido_no_rompe() -> None:
    bueno = _Capturador()
    svc = _servicio([_CanalCaido(), bueno])
    await svc.despachar(_alerta(SeveridadSeguridad.CRITICA))
    assert len(bueno.recibidas) == 1


def test_procesar_sin_loop_no_falla() -> None:
    # Sin event loop en curso el despacho async no ocurre, pero no lanza excepcion.
    svc = _servicio([_Capturador()])
    svc.procesar(_alerta(SeveridadSeguridad.ALTA))


def _record(evento: str, severidad: str) -> logging.LogRecord:
    record = logging.LogRecord(
        "sufi.seguridad", logging.ERROR, __file__, 1, "msg", None, None
    )
    record.evento_seguridad = evento  # type: ignore[attr-defined]
    record.severidad = severidad  # type: ignore[attr-defined]
    record.actor = "jperez"  # type: ignore[attr-defined]
    record.ip = "203.0.113.9"  # type: ignore[attr-defined]
    record.resultado = "fallo"  # type: ignore[attr-defined]
    return record


def test_handler_deriva_alerta_de_record() -> None:
    alerta = alerta_desde_record(_record("autenticacion", "alta"))
    assert alerta is not None
    assert alerta.severidad is SeveridadSeguridad.ALTA
    assert alerta.actor == "jperez"


def test_handler_ignora_eventos_del_propio_alertador() -> None:
    assert alerta_desde_record(_record("alerta_emitida", "alta")) is None
    assert alerta_desde_record(_record("alerta_canal_log", "critica")) is None


def test_handler_emite_al_servicio_sin_romper_logging() -> None:
    cap = _Capturador()
    svc = _servicio([cap])
    handler = AlertaHandler(svc)
    # emit no debe lanzar; sin loop en curso el gating pasa pero el despacho async se omite.
    handler.emit(_record("autorizacion", "alta"))


def test_webhook_payload() -> None:
    n = NotificadorWebhook("https://hooks.example/abc")
    p = n.payload(_alerta(SeveridadSeguridad.CRITICA))
    assert p["severidad"] == "critica"
    assert p["actor"] == "jperez"
    assert p["correlation_id"] == "req-1"


async def test_correo_alerta_envia_al_destino() -> None:
    fake = _CorreoFake()
    n = NotificadorCorreoAlerta(fake, "soc@sufi.co")
    await n.alertar(_alerta(SeveridadSeguridad.ALTA))
    assert fake.enviados[0][0] == "soc@sufi.co"