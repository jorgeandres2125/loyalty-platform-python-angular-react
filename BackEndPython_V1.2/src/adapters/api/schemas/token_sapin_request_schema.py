from pydantic import BaseModel


class TokenSAPINRequest(BaseModel):
    cedula: str
    alianza: str
