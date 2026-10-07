from __future__ import annotations


class OtpRequerido(Exception):
    """AP-0012: la autenticacion exige un segundo factor OTP; se emitio un desafio.

    No es un error: interrumpe la emision del token en el paso 1 del login para exigir el
    OTP. Lleva el identificador del desafio y el correo enmascarado al que se envio.
    """

    def __init__(
        self, desafio_id: str, email_enmascarado: str, expira_en_segundos: int
    ) -> None:
        super().__init__("otp requerido")
        self.desafio_id: str = desafio_id
        self.email_enmascarado: str = email_enmascarado
        self.expira_en_segundos: int = expira_en_segundos
