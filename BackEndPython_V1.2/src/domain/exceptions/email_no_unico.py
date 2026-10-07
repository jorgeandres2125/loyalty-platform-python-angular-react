from __future__ import annotations


class EmailNoUnico(Exception):
    """El correo ya esta registrado por otro usuario (AP-0141: unicidad)."""

    def __init__(self, email: str, numero_documento: str) -> None:
        super().__init__(
            f"El correo '{email}' ya esta registrado por otro usuario."
        )
        self.email: str = email
        self.numero_documento: str = numero_documento
