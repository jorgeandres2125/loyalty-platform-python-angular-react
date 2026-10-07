from __future__ import annotations

from typing import Final

import bcrypt

# AP-0160: hash dummy pre-computado una sola vez al iniciar el proceso.
# Se usa para ejecutar siempre una comparacion bcrypt cuando el usuario no existe.
_TIMING_GUARD: Final[str] = bcrypt.hashpw(
    b"___SUFI_TIMING_GUARD___",
    bcrypt.gensalt(rounds=12),
).decode("utf-8")


class PasswordHasher:
    def hashear(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

    def verificar(self, password: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False

    def verificar_dummy(self, password: str) -> None:
        # AP-0160: ejecuta bcrypt dummy para igualar tiempos cuando el usuario no existe.
        self.verificar(password, _TIMING_GUARD)
