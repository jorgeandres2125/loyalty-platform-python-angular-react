from __future__ import annotations


class EmailInvalido(ValueError):
    """El correo no cumple la estructura de direccion RFC822 (AP-0141)."""

    def __init__(self, valor: str) -> None:
        super().__init__(
            f"El correo '{valor}' no tiene un formato valido (RFC822)."
        )
        self.valor: str = valor
