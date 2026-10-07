from pydantic import BaseModel


class DocumentoUploadRequest(BaseModel):
    """tipo: 4=Cédula, 5=RUT, 6=Contrato."""
    numero_documento: str
    tipo: int
    nombre: str = ""
