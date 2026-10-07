from __future__ import annotations

import re
from typing import Final

from src.domain.exceptions.email_invalido import EmailInvalido

# AP-0141: estructura de direccion RFC822 (local@dominio.tld). Validacion
# pragmatica que cubre la inmensa mayoria de direcciones reales.
_PATRON_RFC822: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
)
_MAX_LONGITUD: Final[int] = 254


class Email:
    """Direccion de correo validada (RFC822), inmutable y normalizada a minusculas.

    Lanza EmailInvalido si el formato no cumple. Se usa en el registro de usuarios
    para garantizar validez (AP-0141) y normalizar antes de comparar unicidad.
    """

    __slots__ = ("_valor",)

    def __init__(self, valor: str) -> None:
        normalizado: str = (valor or "").strip().lower()
        if (
            not normalizado
            or len(normalizado) > _MAX_LONGITUD
            or _PATRON_RFC822.match(normalizado) is None
        ):
            raise EmailInvalido(valor)
        self._valor: str = normalizado

    @property
    def valor(self) -> str:
        return self._valor

    def __str__(self) -> str:
        return self._valor
