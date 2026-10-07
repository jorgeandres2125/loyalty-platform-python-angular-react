from dataclasses import dataclass


@dataclass
class ModerarDocumentoDTO:
    documento_id: int
    estado: str   # aprobado | rechazado
    uid_moderador: int
    observacion: str = ""
