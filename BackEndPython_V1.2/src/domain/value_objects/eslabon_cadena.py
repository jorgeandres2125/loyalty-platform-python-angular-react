from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EslabonCadena:
    """AP-0025: un eslabon del sello encadenado de un evento de auditoria.

    Cada evento sellado produce un eslabon inmutable: su numero de secuencia, el hash
    del contenido del evento, el hash del eslabon anterior y el hash resultante que
    encadena ambos. La cadena completa es verificable: alterar, insertar o eliminar un
    evento rompe la continuidad de los hashes de forma detectable (tamper-evidence).
    """

    secuencia: int
    hash_previo: str
    hash_contenido: str
    hash_actual: str
