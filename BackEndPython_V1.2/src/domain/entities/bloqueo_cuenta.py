from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class BloqueoCuenta:
    """AP-0009: estado de bloqueo de una cuenta por intentos fallidos de login.

    Inmutable, indexado por la clave de cuenta (nombre de usuario normalizado). Guarda
    el contador de fallos consecutivos, si esta bloqueada y (para el desbloqueo
    automatico) el instante de bloqueo y de expiracion en segundos epoch. expira == 0
    significa bloqueo permanente (sin desbloqueo automatico).
    """

    clave: str
    conteo_fallos: int
    bloqueada: bool
    bloqueada_en_epoch: float
    expira_en_epoch: float
    motivo: str = ""

    @classmethod
    def inicial(cls, clave: str) -> BloqueoCuenta:
        return cls(
            clave=clave,
            conteo_fallos=0,
            bloqueada=False,
            bloqueada_en_epoch=0.0,
            expira_en_epoch=0.0,
        )

    def con_fallo(self) -> BloqueoCuenta:
        return replace(self, conteo_fallos=self.conteo_fallos + 1)

    def bloqueada_hasta(self, ahora: float, expira: float) -> BloqueoCuenta:
        return replace(
            self, bloqueada=True, bloqueada_en_epoch=ahora, expira_en_epoch=expira
        )

    def con_motivo(self, motivo: str) -> BloqueoCuenta:
        return replace(self, motivo=motivo)
