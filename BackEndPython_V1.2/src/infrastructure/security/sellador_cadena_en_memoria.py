from __future__ import annotations

import threading
import uuid

from src.domain.services.calculadora_hash_cadena import CalculadoraHashCadena
from src.domain.value_objects.eslabon_cadena import EslabonCadena


class SelladorCadenaEnMemoria:
    """AP-0025: sellador encadenado en memoria, seguro ante concurrencia.

    Mantiene el estado de una cadena por proceso (ultimo hash y numero de secuencia) e
    identifica la cadena con un id generado al arrancar, para que el verificador sepa a
    que instancia pertenecen los eslabones. Satisface el puerto SelladorLog (PEP 544).
    Cada peticion de sellado avanza la cadena bajo un lock, de modo que dos hilos nunca
    comparten un mismo numero de secuencia.
    """

    def __init__(self) -> None:
        self._calc: CalculadoraHashCadena = CalculadoraHashCadena()
        self._lock: threading.Lock = threading.Lock()
        self._secuencia: int = 0
        self._hash_previo: str = self._calc.genesis()
        self._cadena_id: str = uuid.uuid4().hex

    @property
    def cadena_id(self) -> str:
        return self._cadena_id

    def sellar(self, contenido: str) -> EslabonCadena:
        hash_contenido: str = self._calc.hash_contenido(contenido)
        with self._lock:
            hash_previo: str = self._hash_previo
            secuencia: int = self._secuencia
            hash_actual: str = self._calc.encadenar(hash_previo, hash_contenido)
            self._hash_previo = hash_actual
            self._secuencia = secuencia + 1
        return EslabonCadena(
            secuencia=secuencia,
            hash_previo=hash_previo,
            hash_contenido=hash_contenido,
            hash_actual=hash_actual,
        )
