from __future__ import annotations

from src.domain.value_objects.canal_oob import CanalOob
from src.domain.value_objects.tipo_transaccion_critica import TipoTransaccionCritica


class ClasificadorCriticidad:
    """AP-0005: motor de riesgo (version MVP) que clasifica una transaccion.

    Decide si una operacion exige confirmacion OOB. En esta fase la decision es por
    catalogo: todo tipo reconocido en TipoTransaccionCritica es critico y requiere OOB.
    Fail-secure: un tipo desconocido NO se degrada a critico, se deja pasar a los
    controles de capa 7. El canal por defecto es el correo (reutiliza AP-0004); fases
    posteriores anaden puntuacion por senales (IP, dispositivo, horario, frecuencia) y
    seleccion de canal fuerte (SMS o push).
    """

    def tipo_desde(self, valor: str) -> TipoTransaccionCritica | None:
        try:
            return TipoTransaccionCritica(valor)
        except ValueError:
            return None

    def requiere_oob(self, tipo: TipoTransaccionCritica | None) -> bool:
        return tipo is not None

    def canal_para(self, tipo: TipoTransaccionCritica) -> CanalOob:
        return CanalOob.CORREO
