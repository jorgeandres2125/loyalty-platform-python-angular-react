from pydantic import BaseModel


class TokenSAPINResponse(BaseModel):
    token: str
    cedula: str
    url_sapin: str = ""
