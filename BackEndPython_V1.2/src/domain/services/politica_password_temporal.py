from __future__ import annotations

from datetime import datetime, timedelta

from src.domain.entities.password_temporal_entity import PasswordTemporalEntity
from src.domain.value_objects.estado_password_temporal import EstadoPasswordTemporal


class PoliticaPasswordTemporal:
    """AP-0048: politica pura de vigencia de contrasenas temporales.

    El TTL es una DURACION (maximo 120 minutos), no una fecha calendario: toda la
    aritmetica es UTC naive (convencion del proyecto) y la zona horaria de negocio
    solo participa al mostrar la hora al usuario. La comparacion en el limite es
    estricta: en el instante exacto de expira_iso la temporal AUN es valida.
    """

    def __init__(self, ttl_minutos: int) -> None:
        self._ttl_minutos: int = ttl_minutos

    def calcular_expiracion(self, emitida: datetime) -> datetime:
        return emitida + timedelta(minutes=self._ttl_minutos)

    @staticmethod
    def esta_vencida(entidad: PasswordTemporalEntity, ahora: datetime) -> bool:
        return ahora > datetime.fromisoformat(entidad.expira_iso)

    def puede_autenticar(
        self, entidad: PasswordTemporalEntity, ahora: datetime
    ) -> bool:
        # ACTIVA o USADA (no consumida ni reemplazada) y dentro de la vigencia.
        if entidad.estado not in (
            EstadoPasswordTemporal.ACTIVA,
            EstadoPasswordTemporal.USADA,
        ):
            return False
        return not self.esta_vencida(entidad, ahora)
