"""Constantes de la verificación de propiedad del correo (AP-0004).

Política numérica configurable (TTL, intentos, cooldown) vive en
`infrastructure/config/settings.py` para poder ajustarse por entorno; aquí solo
quedan los valores fijos del contrato del flujo.
"""
from typing import Final

from src.shared.constants.otp import validar_longitud_otp

# Longitud exacta del código OTP enviado por correo (8 dígitos → espacio 10^8).
CODIGO_LONGITUD: Final[int] = validar_longitud_otp(8, "CODIGO_LONGITUD")

# Etiqueta del evento en historico_correo (log de correos enviados).
TIPO_CORREO_VERIFICACION: Final[str] = "VERIFICACION_EMAIL"

# Remitente lógico registrado en historico_correo.usuario_envio.
REMITENTE_SISTEMA: Final[str] = "sistema"

ASUNTO_VERIFICACION: Final[str] = "Verifica tu correo — SUFI Siempre a tu lado"
