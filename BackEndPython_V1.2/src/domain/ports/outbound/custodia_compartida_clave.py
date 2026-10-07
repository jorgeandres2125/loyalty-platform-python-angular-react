from __future__ import annotations

from typing import Protocol


class CustodiaCompartidaClave(Protocol):
    """AP-0015: reparto de una clave secreta entre varios custodios (secret sharing).

    Contrato estructural (PEP 544). `dividir` reparte un secreto (la KEK) en `total`
    fragmentos (shares) con un umbral; se necesitan `umbral` shares para reconstruir el
    secreto, y menos de esos no revelan nada. `reconstruir` recupera el secreto a partir
    de al menos `umbral` shares. Permite que ninguna persona sola posea o reconstruya la
    clave.
    """

    def dividir(self, secreto: bytes, total: int, umbral: int) -> list[bytes]: ...
    def reconstruir(self, shares: list[bytes]) -> bytes: ...
