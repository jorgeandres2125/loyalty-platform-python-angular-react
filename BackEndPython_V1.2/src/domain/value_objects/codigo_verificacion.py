from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CodigoVerificacion:
    """Registro inmutable de un código OTP de verificación de correo (AP-0004).

    Solo se conserva el hash del código (sha256), nunca el valor en claro: un
    volcado de memoria o un log accidental no debe exponer el OTP. `intentos_restantes`
    decrementa con cada confirmación fallida; al llegar a 0 el código se invalida.
    `creado_en_monotonic` (reloj monótono) sostiene el cooldown de reenvío.
    """

    codigo_hash: str
    intentos_restantes: int
    creado_en_monotonic: float

    def con_intento_consumido(self) -> CodigoVerificacion:
        return CodigoVerificacion(
            codigo_hash=self.codigo_hash,
            intentos_restantes=self.intentos_restantes - 1,
            creado_en_monotonic=self.creado_en_monotonic,
        )
