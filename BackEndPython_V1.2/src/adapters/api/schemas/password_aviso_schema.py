from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PasswordAvisoSchema(BaseModel):
    """AP-0037: aviso de vencimiento de contrasena expuesto al frontend.

    Solo aparece en la respuesta cuando el vencimiento cae dentro de la ventana de
    aviso (por defecto 7 dias); de lo contrario el campo padre es null y no se
    notifica. El frontend arma el mensaje (singular, plural o manana) a partir de
    dias_restantes.
    """

    model_config = ConfigDict(extra="forbid")

    dias_restantes: int
    fecha_expiracion: str
