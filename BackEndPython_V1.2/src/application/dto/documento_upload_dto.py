from dataclasses import dataclass


@dataclass
class DocumentoUploadDTO:
    """tipo: 4=Cédula, 5=RUT, 6=Contrato."""
    numero_documento: str
    tipo: int
    nombre: str = ""
