from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TokenSAPIN:
    token_cifrado: str
    cedula: str
    generado_en: datetime

    def __str__(self) -> str:
        return self.token_cifrado
