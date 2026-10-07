from __future__ import annotations

from dataclasses import dataclass, replace

from src.domain.value_objects.canal_oob import CanalOob
from src.domain.value_objects.estado_desafio_oob import EstadoDesafioOob
from src.domain.value_objects.tipo_transaccion_critica import TipoTransaccionCritica


@dataclass(frozen=True)
class DesafioOob:
    """AP-0005: desafio de confirmacion fuera de banda de una transaccion critica.

    Agregado inmutable. Liga el desafio a la operacion exacta por `payload_hash`
    (SHA-256 del payload): aprobar un desafio no habilita ejecutar otra operacion.
    Solo se guarda el hash del codigo, nunca el valor en claro. Las transiciones se
    hacen sobre un desafio PENDIENTE (un desafio ya resuelto no se re-resuelve; lo
    verifica el caso de uso via `es_resoluble`).
    """

    desafio_id: str
    uid: str
    tipo_transaccion: TipoTransaccionCritica
    canal: CanalOob
    payload_hash: str
    codigo_hash: str
    intentos_restantes: int
    creado_en_monotonic: float
    estado: EstadoDesafioOob

    @property
    def es_resoluble(self) -> bool:
        return self.estado is EstadoDesafioOob.PENDIENTE

    def con_intento_consumido(self) -> DesafioOob:
        return replace(self, intentos_restantes=self.intentos_restantes - 1)

    def aprobado(self) -> DesafioOob:
        return replace(self, estado=EstadoDesafioOob.APROBADA)

    def rechazado(self) -> DesafioOob:
        return replace(self, estado=EstadoDesafioOob.RECHAZADA)

    def bloqueado(self) -> DesafioOob:
        return replace(self, estado=EstadoDesafioOob.BLOQUEADA)
