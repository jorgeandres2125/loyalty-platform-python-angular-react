import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Cedula:
    valor: str

    def __post_init__(self) -> None:
        if not re.match(r"^\d{5,11}$", self.valor):
            raise ValueError(f"Cédula inválida: '{self.valor}'")

    def __str__(self) -> str:
        return self.valor
