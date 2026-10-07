from __future__ import annotations

from src.domain.services.verificador_cadena import VerificadorCadena
from src.domain.value_objects.eslabon_cadena import EslabonCadena
from src.domain.value_objects.resultado_verificacion_cadena import ResultadoVerificacionCadena


class VerificarIntegridadCadenaUseCase:
    """AP-0025: caso de uso que verifica la integridad de una cadena de sellos.

    Recibe la secuencia de eslabones tal como quedo almacenada en el destino inmutable
    y delega en el verificador de dominio. Permite que un auditor demuestre, sin acceso
    al codigo, que los eventos no fueron alterados, insertados ni eliminados.
    """

    def __init__(self, verificador: VerificadorCadena) -> None:
        self._verificador: VerificadorCadena = verificador

    def ejecutar(self, eslabones: list[EslabonCadena]) -> ResultadoVerificacionCadena:
        return self._verificador.verificar(eslabones)
