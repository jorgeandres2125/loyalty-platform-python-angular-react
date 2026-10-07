from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class DesafioOtpLogin:
    """AP-0012: desafio OTP del segundo factor en el proceso de autenticacion (login).

    Inmutable, indexado por desafio_id. Solo guarda el hash del codigo (nunca el valor en
    claro). El codigo es de un solo uso: al verificarlo con exito el desafio se elimina del
    almacen, de modo que no puede reutilizarse. intentos_restantes decrementa con cada
    intento fallido; agotados, el desafio se invalida.
    """

    desafio_id: str
    uid: int
    codigo_hash: str
    intentos_restantes: int
    creado_en_monotonic: float

    def con_intento_consumido(self) -> DesafioOtpLogin:
        return replace(self, intentos_restantes=self.intentos_restantes - 1)
