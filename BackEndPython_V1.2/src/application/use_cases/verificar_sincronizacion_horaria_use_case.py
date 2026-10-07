from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from src.application.dto.estado_sincronizacion_dto import EstadoSincronizacionDTO
from src.domain.ports.outbound.reloj_oficial import RelojOficial


def _ahora_utc() -> datetime:
    return datetime.now(UTC)


class VerificarSincronizacionHorariaUseCase:
    """AP-0144: verifica que la hora del sistema este sincronizada con la hora
    oficial del pais. Compara el reloj local con un reloj externo confiable y
    calcula el desfase; `sincronizado` es True si no supera el umbral."""

    def __init__(
        self,
        reloj: RelojOficial,
        umbral_segundos: int,
        clock: Callable[[], datetime] = _ahora_utc,
    ) -> None:
        self._reloj: RelojOficial = reloj
        self._umbral_segundos: int = umbral_segundos
        self._clock: Callable[[], datetime] = clock

    async def ejecutar_async(self) -> EstadoSincronizacionDTO:
        oficial: datetime = await self._reloj.obtener_hora_oficial_async()
        sistema: datetime = self._clock()
        desfase: float = abs((oficial - sistema).total_seconds())
        return EstadoSincronizacionDTO(
            hora_sistema=sistema,
            hora_oficial=oficial,
            desfase_segundos=desfase,
            sincronizado=desfase <= self._umbral_segundos,
            umbral_segundos=self._umbral_segundos,
        )
