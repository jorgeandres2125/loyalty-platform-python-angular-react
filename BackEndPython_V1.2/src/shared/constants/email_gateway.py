"""Constantes del gateway HTTP de correo ('email-send-on-demand').

Las URLs base cambian por ambiente y viven en `infrastructure/config/settings.py`
(`email_api_*`); aquí solo quedan las rutas fijas del contrato del proveedor.
"""
from typing import Final

# Ruta del login que devuelve el authToken JWT.
EMAIL_AUTH_PATH: Final[str] = "/management/api/v1/auth/login"

# Ruta del envío de correo. El doble slash es parte del contrato del gateway
# (prefijo de enrutado 'email-send-on-demand/' + path del servicio '/api/...').
EMAIL_SEND_PATH: Final[str] = "/email-send-on-demand//api/v1/email/send"

# Margen (segundos) antes de la expiración real para renovar el token de forma
# proactiva y evitar usar uno a punto de vencer.
TOKEN_MARGEN_EXPIRACION_SEG: Final[int] = 60
