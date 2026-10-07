from __future__ import annotations


class CredencialVigente(Exception):
    """AP-0038: se intento el cambio autonomo por vencimiento sobre una contrasena vigente.

    El endpoint de cambio por vencimiento es exclusivo para contrasenas vencidas dentro
    de la gracia; si la contrasena sigue vigente el usuario debe usar el cambio estandar.
    """

    def __init__(self) -> None:
        super().__init__("la contrasena sigue vigente")
