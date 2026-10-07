from __future__ import annotations

from collections.abc import Sequence

from src.domain.exceptions.password_insegura import PasswordInsegura


class ValidadorPassword:
    """Servicio de dominio: valida que una contrasena no sea comun ni contextualmente
    debil (AP-0159).

    Separado de los validadores de longitud/complejidad (AP-0044, AP-0051) para que
    cada control tenga un punto de cambio unico. Sin dependencias de framework.
    """

    def __init__(self, blacklist: frozenset[str]) -> None:
        self._blacklist: frozenset[str] = blacklist

    # ── API publica ───────────────────────────────────────────────────────────

    def validar(
        self,
        password: str,
        valores_contextuales: Sequence[str] | None = None,
    ) -> None:
        """Lanza PasswordInsegura si la contrasena es insegura o contextualmente debil.

        Checks en orden:
        1. Blacklist de contrasenas comunes (case-insensitive).
        2. Coincidencia con valores del contexto del usuario (nombre, cedula, email).
           Se rechaza si la contrasena es igual, contiene o esta contenida en el valor.
        """
        pwd_lower: str = password.lower().strip()

        if pwd_lower in self._blacklist:
            raise PasswordInsegura(
                "La contrasena es demasiado comun o conocida como insegura. "
                "Elige una contrasena unica que no aparezca en diccionarios conocidos."
            )

        if valores_contextuales:
            for valor in valores_contextuales:
                if not valor:
                    continue
                val_lower: str = valor.lower().strip()
                if not val_lower:
                    continue
                if pwd_lower == val_lower or val_lower in pwd_lower or pwd_lower in val_lower:
                    raise PasswordInsegura(
                        "La contrasena no puede contener el nombre de usuario, "
                        "numero de documento u otros datos personales identificables."
                    )

    def en_blacklist(self, password: str) -> bool:
        """True si la contrasena (case-insensitive) esta en la blacklist."""
        return password.lower().strip() in self._blacklist
