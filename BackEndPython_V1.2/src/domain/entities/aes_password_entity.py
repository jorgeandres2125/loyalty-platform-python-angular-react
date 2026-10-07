from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AesPasswordEntity:
    """Contraseña cifrada AES — tabla aes_passwords."""
    uid: int = 0
    pass_: str = ""
