from __future__ import annotations

from typing import Protocol

from src.domain.value_objects.eslabon_cadena import EslabonCadena


class SelladorLog(Protocol):
    """AP-0025: puerto de sellado encadenado de eventos (tamper-evidence en origen).

    Un adaptador sella cada evento de auditoria produciendo un EslabonCadena que enlaza
    el evento con el anterior. La implementacion mantiene el estado de la cadena (ultimo
    hash y numero de secuencia) de forma segura ante concurrencia.
    """

    def sellar(self, contenido: str) -> EslabonCadena: ...
