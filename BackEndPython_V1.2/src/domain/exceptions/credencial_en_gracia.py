from __future__ import annotations


class CredencialEnGracia(Exception):
    """AP-0038: la contrasena esta vencida pero dentro de la ventana de gracia.

    No es un error de credenciales: el hash es correcto. Interrumpe la emision de la
    sesion plena en el login para exigir el cambio autonomo por vencimiento. Lleva los
    dias transcurridos desde el vencimiento y los dias de gracia restantes.
    """

    def __init__(self, dias_desde_vencimiento: int, dias_restantes_gracia: int) -> None:
        super().__init__("credencial vencida en periodo de gracia")
        self.dias_desde_vencimiento: int = dias_desde_vencimiento
        self.dias_restantes_gracia: int = dias_restantes_gracia
