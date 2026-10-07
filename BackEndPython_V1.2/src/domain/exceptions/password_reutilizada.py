from __future__ import annotations


class PasswordReutilizada(ValueError):
    """AP-0041: la nueva contrasena coincide con una de las ultimas N usadas.

    Se rechaza el cambio para impedir la reutilizacion de contrasenas recientes.
    """

    def __init__(self, tamano: int = 24) -> None:
        super().__init__(
            "La nueva contrasena coincide con una de las ultimas "
            + str(tamano)
            + " que usaste. Elige una que no hayas utilizado recientemente."
        )
        self.tamano: int = tamano
