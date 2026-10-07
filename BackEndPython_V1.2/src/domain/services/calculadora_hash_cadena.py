from __future__ import annotations

import hashlib

from src.shared.constants.cadena_log import HASH_GENESIS


class CalculadoraHashCadena:
    """AP-0025: primitivas de hash de la cadena de sellos (sin estado ni framework).

    Centraliza el algoritmo para que el sellador (en origen) y el verificador (en
    auditoria) produzcan exactamente el mismo hash. El encadenamiento es
    hash_actual = SHA-256(hash_previo + hash_contenido), y el primer eslabon usa
    HASH_GENESIS como hash_previo.
    """

    @staticmethod
    def genesis() -> str:
        return HASH_GENESIS

    @staticmethod
    def hash_contenido(contenido: str) -> str:
        return hashlib.sha256(contenido.encode("utf-8")).hexdigest()

    @staticmethod
    def encadenar(hash_previo: str, hash_contenido: str) -> str:
        material: str = hash_previo + hash_contenido
        return hashlib.sha256(material.encode("utf-8")).hexdigest()
