from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Final

import httpx

# Claves comunes donde las APIs publicas de fecha/hora ubican el valor ISO.
_CLAVES_FECHA: Final[tuple[str, ...]] = (
    "datetime",
    "dateTime",
    "currentDateTime",
    "date_time",
    "utc_datetime",
    "now",
    "time",
)


class RelojOficialHttp:
    """AP-0144: obtiene la hora oficial desde una API publica de fecha/hora.

    Satisface el puerto RelojOficial (PEP 544). Es tolerante al formato de la
    respuesta (JSON con varias claves posibles, o texto ISO plano) y devuelve un
    datetime con zona horaria.
    """

    def __init__(
        self,
        url: str,
        timeout: int,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._url: str = url
        self._timeout: int = timeout
        self._transport: httpx.AsyncBaseTransport | None = transport

    def _abrir_cliente(self) -> httpx.AsyncClient:
        if self._transport is not None:
            return httpx.AsyncClient(timeout=self._timeout, transport=self._transport)
        return httpx.AsyncClient(timeout=self._timeout)

    async def obtener_hora_oficial_async(self) -> datetime:
        async with self._abrir_cliente() as cliente:
            respuesta: httpx.Response = await cliente.get(self._url)
            respuesta.raise_for_status()
            return self._extraer_datetime(respuesta)

    @classmethod
    def _extraer_datetime(cls, respuesta: httpx.Response) -> datetime:
        crudo: str | None = cls._buscar_texto(respuesta)
        if crudo is None:
            raise ValueError("La API de hora oficial no devolvio una fecha reconocible.")
        return cls._parsear(crudo)

    @classmethod
    def _buscar_texto(cls, respuesta: httpx.Response) -> str | None:
        try:
            datos: Any = respuesta.json()
        except ValueError:
            texto: str = respuesta.text.strip()
            return texto or None
        if isinstance(datos, str):
            return datos
        if isinstance(datos, dict):
            for clave in _CLAVES_FECHA:
                valor: Any = datos.get(clave)
                if isinstance(valor, str) and valor:
                    return valor
        return None

    @staticmethod
    def _parsear(crudo: str) -> datetime:
        texto: str = crudo.strip().replace("Z", "+00:00")
        momento: datetime = datetime.fromisoformat(texto)
        if momento.tzinfo is None:
            momento = momento.replace(tzinfo=UTC)
        return momento
