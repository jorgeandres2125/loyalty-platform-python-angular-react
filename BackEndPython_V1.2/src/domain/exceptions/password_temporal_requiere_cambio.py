from __future__ import annotations


class PasswordTemporalRequiereCambio(Exception):
    """AP-0046: el login presento una contrasena temporal valida y vigente.

    No es un error de credenciales: el hash temporal coincide. Se interrumpe la
    emision de la sesion plena para exigir el cambio obligatorio por el endpoint
    dedicado. Lleva la expiracion para informar la ventana restante al usuario.
    """

    def __init__(self, expira_iso: str) -> None:
        super().__init__("contrasena temporal: requiere cambio obligatorio")
        self.expira_iso: str = expira_iso
