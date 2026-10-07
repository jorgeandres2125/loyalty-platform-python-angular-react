from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AvisoExpiracionPassword:
    """AP-0037: aviso de que la contrasena esta por vencer.

    Solo se construye cuando el vencimiento cae dentro de la ventana de aviso
    (ver PoliticaExpiracionPassword). `dias_restantes` es un entero positivo
    (1 = vence manana); el frontend arma el texto singular o plural a partir de el.
    `fecha_expiracion_iso` es la fecha de vencimiento en formato ISO-8601 (solo
    fecha), util para trazabilidad y para mostrarla si se desea.
    """

    dias_restantes: int
    fecha_expiracion_iso: str
