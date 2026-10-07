from __future__ import annotations

from dataclasses import dataclass

from src.domain.value_objects.severidad_seguridad import SeveridadSeguridad


@dataclass
class AlertaSeguridad:
    """AP-0134: alerta derivada de un evento de seguridad sensible. Lleva solo campos no
    secretos (el evento origen ya viene redactado, AP-0087) y el correlation_id para
    trazar de extremo a extremo el evento, la alerta y la respuesta."""

    titulo: str
    severidad: SeveridadSeguridad
    evento: str
    resultado: str
    actor: str
    ip: str
    correlation_id: str
    detalle: str | None = None

    @property
    def clave_dedup(self) -> str:
        return self.evento + "|" + self.resultado + "|" + self.actor + "|" + self.ip
