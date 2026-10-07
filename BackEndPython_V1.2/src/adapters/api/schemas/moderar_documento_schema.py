from pydantic import BaseModel


class ModerarDocumentoRequest(BaseModel):
    documento_id: int
    estado: str
    observacion: str = ""
