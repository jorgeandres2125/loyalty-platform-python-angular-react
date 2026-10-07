from __future__ import annotations

from typing import Protocol


class AlmacenEfimeroDistribuido(Protocol):
    """AP-0081: puerto de almacen efimero compartido entre replicas (clave-valor con TTL).

    Habilita la alta disponibilidad multi-replica de los estados efimeros (OTP, desafios
    OOB, contadores de throttle): con dos o mas replicas, un estado guardado por una replica
    debe ser legible por las demas. Un adaptador Redis satisface este contrato en produccion;
    el adaptador en memoria sirve para un unico proceso (desarrollo y pruebas). Contrato
    estructural (PEP 544): el adaptador cumple por forma, sin heredar.
    """

    async def guardar(self, clave: str, valor: str, ttl_segundos: int) -> None:
        ...

    async def obtener(self, clave: str) -> str | None:
        ...

    async def eliminar(self, clave: str) -> None:
        ...
