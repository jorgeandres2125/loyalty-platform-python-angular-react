from __future__ import annotations

from enum import StrEnum


class EstadoPasswordTemporal(StrEnum):
    """AP-0046, AP-0047 y AP-0048: ciclo de vida de una contrasena temporal.

    - ACTIVA: emitida y aun sin usar.
    - USADA: ya autentico al menos un login; solo habilita el cambio obligatorio.
    - CONSUMIDA: el cambio obligatorio se completo; terminal.
    - REEMPLAZADA: una emision posterior la invalido; terminal.

    El vencimiento (AP-0048) es DERIVADO: una fila ACTIVA o USADA cuya expira_iso
    ya paso se comporta como vencida sin cambiar de estado persistido.
    """

    ACTIVA = "activa"
    USADA = "usada"
    CONSUMIDA = "consumida"
    REEMPLAZADA = "reemplazada"
