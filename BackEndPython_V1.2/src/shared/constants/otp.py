from typing import Final

# AP-0135: longitud minima de un OTP (OWASP ASVS V2.8). Piso inmutable garantizado por
# codigo: ninguna longitud de OTP puede quedar por debajo de este valor.
OTP_LONGITUD_MINIMA: Final[int] = 6

# AP-0136: validez maxima (en segundos) de un OTP de autenticacion o autorizacion.
OTP_TTL_MAXIMO_SEG: Final[int] = 60


def validar_longitud_otp(longitud: int, nombre: str) -> int:
    """AP-0135: garantiza (fail-fast en import) que una longitud de OTP no baje del piso."""
    if longitud < OTP_LONGITUD_MINIMA:
        raise ValueError(
            f"{nombre}={longitud} viola AP-0135: la longitud minima de un OTP es "
            f"{OTP_LONGITUD_MINIMA}."
        )
    return longitud
