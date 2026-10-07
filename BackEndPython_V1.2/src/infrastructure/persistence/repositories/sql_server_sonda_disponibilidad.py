from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

_logger: logging.Logger = logging.getLogger(__name__)


class SqlServerSondaDisponibilidad:
    """AP-0081: adaptador que verifica la conectividad con la base de datos con un
    SELECT 1 minimo. Implementa SondaDisponibilidad (PEP 544). Usa la fabrica de
    sesiones autonoma (independiente de la peticion). Nunca propaga la excepcion:
    ante cualquier fallo devuelve False para que la sonda de readiness saque la
    replica del balanceo sin tumbar el proceso.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession] | None) -> None:
        self._session_factory: async_sessionmaker[AsyncSession] | None = session_factory

    async def base_datos_disponible(self) -> bool:
        if self._session_factory is None:
            return False
        try:
            async with self._session_factory() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception:
            _logger.warning("AP-0081: readiness -- base de datos no disponible")
            return False
