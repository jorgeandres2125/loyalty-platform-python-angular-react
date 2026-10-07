class CifradoError(Exception):
    """Fallo al cifrar o descifrar un campo restringido (clave incorrecta, AAD
    no coincidente o criptograma manipulado — tag GCM inválido)."""

    def __init__(self, detalle: str = "") -> None:
        super().__init__(f"Error de cifrado de campo: {detalle}")
