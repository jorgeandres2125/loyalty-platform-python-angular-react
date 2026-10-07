class TokenInvalido(Exception):
    def __init__(self, detalle: str = "") -> None:
        super().__init__(f"Token inválido: {detalle}")
