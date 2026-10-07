from dataclasses import dataclass


@dataclass
class TokenSAPINResponseDTO:
    token: str
    cedula: str
    url_sapin: str = ""
