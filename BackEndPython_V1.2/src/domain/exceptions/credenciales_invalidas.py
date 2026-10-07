class CredencialesInvalidas(Exception):
    """Credenciales de login inválidas (usuario inexistente o contraseña incorrecta).

    El caso de uso ya aplicó el retraso incremental (AP-0007) antes de lanzarla; el
    adaptador HTTP la traduce a 401 sin distinguir entre usuario inexistente y
    contraseña errónea (no abre un canal de enumeración de usuarios).
    """

    def __init__(self, detalle: str = "") -> None:
        super().__init__(detalle or "Credenciales incorrectas")
