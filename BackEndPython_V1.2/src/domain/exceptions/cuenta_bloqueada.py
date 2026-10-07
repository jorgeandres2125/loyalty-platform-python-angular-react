from __future__ import annotations


class CuentaBloqueada(Exception):
    """AP-0009: la cuenta esta bloqueada por multiples intentos fallidos de login."""

    def __init__(self, segundos_restantes: int | None = None) -> None:
        super().__init__("cuenta bloqueada")
        self.segundos_restantes: int | None = segundos_restantes
