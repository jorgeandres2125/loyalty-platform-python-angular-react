"""Constantes del OTP de un solo uso en el proceso de autenticacion (AP-0012)."""
from typing import Final

from src.shared.constants.otp import validar_longitud_otp

# Longitud del codigo OTP de login (6 digitos, TTL corto, un solo uso).
OTP_LOGIN_CODIGO_LONGITUD: Final[int] = validar_longitud_otp(6, "OTP_LOGIN_CODIGO_LONGITUD")

# Asunto del correo con el codigo de acceso.
OTP_LOGIN_ASUNTO: Final[str] = "Tu codigo de acceso - SUFI Siempre a tu lado"

# Evento de auditoria del OTP de login (sobre el logger de seguridad AP-0022).
EVENTO_OTP_LOGIN: Final[str] = "otp_login"

# Valores del claim amr (authentication methods references) del token.
AMR_PASSWORD: Final[str] = "pwd"
AMR_OTP: Final[str] = "otp"

