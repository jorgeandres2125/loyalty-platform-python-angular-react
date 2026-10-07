import re
from dataclasses import dataclass


@dataclass(frozen=True)
class NIT:
    valor: str

    def __post_init__(self) -> None:
        if not re.match(r"^\d{8,11}(-\d)?$", self.valor):
            raise ValueError(f"NIT inválido: '{self.valor}'")

    def __str__(self) -> str:
        return self.valor
