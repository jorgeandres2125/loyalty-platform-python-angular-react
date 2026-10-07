from dataclasses import dataclass
from datetime import datetime


@dataclass
class DocumentoEntity:
    """Documento de identidad/tributario — tabla user_documento.
    tipo: 4=Cédula, 5=RUT, 6=Contrato."""
    numero_documento: str
    nombre: str = ""
    estado: str = "pendiente"
    version: int = 1
    fecha: datetime | None = None
    tipo: int = 0
    did: int | None = None
