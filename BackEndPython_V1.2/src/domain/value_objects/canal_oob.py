from enum import StrEnum


class CanalOob(StrEnum):
    """AP-0005: canal fuera de banda por el que se envia el desafio.

    El MVP usa CORREO (reutiliza el gateway de correo de AP-0004). SMS y PUSH quedan
    declarados para las fases siguientes del subsistema OOB multicanal.
    """

    CORREO = "correo"
    SMS = "sms"
    PUSH = "push"
