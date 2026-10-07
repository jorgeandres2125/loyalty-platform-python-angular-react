from __future__ import annotations

from datetime import datetime
from typing import Protocol


class RelojOficial(Protocol):
    """AP-0144: fuente de la hora oficial del pais (reloj externo confiable)."""

    async def obtener_hora_oficial_async(self) -> datetime: ...
