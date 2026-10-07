from __future__ import annotations

from src.domain.services.calculadora_hash_cadena import CalculadoraHashCadena
from src.domain.value_objects.eslabon_cadena import EslabonCadena
from src.domain.value_objects.resultado_verificacion_cadena import ResultadoVerificacionCadena


class VerificadorCadena:
    """AP-0025: verifica la integridad de una cadena de sellos (puro, sin dependencias).

    Recorre los eslabones en orden y confirma tres invariantes por cada uno: (1) la
    secuencia es consecutiva, (2) el hash_previo coincide con el hash_actual del eslabon
    anterior (o con genesis en el primero) y (3) el hash_actual recalculado a partir de
    hash_previo y hash_contenido coincide con el almacenado. Cualquier alteracion,
    insercion, borrado o reordenamiento rompe alguna invariante.
    """

    def __init__(self) -> None:
        self._calc: CalculadoraHashCadena = CalculadoraHashCadena()

    def verificar(self, eslabones: list[EslabonCadena]) -> ResultadoVerificacionCadena:
        total: int = len(eslabones)
        if total == 0:
            return ResultadoVerificacionCadena(
                integra=True, total=0, primer_roto=None, motivo="cadena vacia"
            )
        hash_esperado_previo: str = self._calc.genesis()
        secuencia_esperada: int = eslabones[0].secuencia
        for eslabon in eslabones:
            if eslabon.secuencia != secuencia_esperada:
                return self._roto(eslabon.secuencia, total, "secuencia no consecutiva")
            if eslabon.hash_previo != hash_esperado_previo:
                return self._roto(eslabon.secuencia, total, "enlace con el anterior roto")
            recalculado: str = self._calc.encadenar(eslabon.hash_previo, eslabon.hash_contenido)
            if recalculado != eslabon.hash_actual:
                return self._roto(eslabon.secuencia, total, "hash del eslabon no coincide")
            hash_esperado_previo = eslabon.hash_actual
            secuencia_esperada += 1
        return ResultadoVerificacionCadena(
            integra=True, total=total, primer_roto=None, motivo="cadena integra"
        )

    @staticmethod
    def _roto(secuencia: int, total: int, motivo: str) -> ResultadoVerificacionCadena:
        return ResultadoVerificacionCadena(
            integra=False, total=total, primer_roto=secuencia, motivo=motivo
        )
