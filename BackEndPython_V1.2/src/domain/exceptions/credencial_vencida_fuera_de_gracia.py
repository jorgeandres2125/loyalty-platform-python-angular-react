from __future__ import annotations


class CredencialVencidaFueraDeGracia(Exception):
    """AP-0038: la contrasena vencio hace mas dias que la ventana de gracia.

    El cambio autonomo por el flujo estandar queda bloqueado; el usuario debe usar el
    restablecimiento asistido (correo o administrador). Lleva los dias transcurridos
    desde el vencimiento para la trazabilidad.
    """

    def __init__(self, dias_desde_vencimiento: int) -> None:
        super().__init__("credencial vencida fuera del periodo de gracia")
        self.dias_desde_vencimiento: int = dias_desde_vencimiento
