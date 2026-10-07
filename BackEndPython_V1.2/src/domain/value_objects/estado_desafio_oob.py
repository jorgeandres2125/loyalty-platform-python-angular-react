from enum import StrEnum


class EstadoDesafioOob(StrEnum):
    """AP-0005: estado de un desafio de confirmacion fuera de banda (OOB).

    Maquina de estados: PENDIENTE es el unico estado resoluble; desde el se transita
    a APROBADA, RECHAZADA, EXPIRADA o BLOQUEADA. EJECUTADA la fija el motor de
    transacciones tras liberar la operacion ya aprobada.
    """

    PENDIENTE = "pendiente"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    EXPIRADA = "expirada"
    BLOQUEADA = "bloqueada"
    EJECUTADA = "ejecutada"
