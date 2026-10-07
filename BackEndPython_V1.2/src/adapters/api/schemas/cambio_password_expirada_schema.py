from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.shared.constants.password_blacklist import BLACKLIST_COMUNES
from src.shared.constants.password_policy import (
    PASSWORD_MIN_LONGITUD_USUARIO_FINAL,
    PASSWORD_MIN_TIPOS_CARACTER,
    contar_tipos_caracter,
)


class CambioPasswordExpiradaRequest(BaseModel):
    """AP-0038: cambio autonomo de contrasena vencida dentro de la gracia (sin sesion).

    Como no hay sesion, se autentica con usuario + contrasena vencida. La nueva
    contrasena cumple las mismas politicas que el cambio estandar (AP-0044 longitud,
    AP-0051 complejidad, AP-0159 blacklist).
    """

    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, description="Nombre de usuario")
    password_actual: str = Field(
        min_length=1, description="Contrasena actual vencida (autenticacion)"
    )
    nueva_password: str = Field(
        min_length=PASSWORD_MIN_LONGITUD_USUARIO_FINAL,
        description=f"Nueva contrasena (minimo {PASSWORD_MIN_LONGITUD_USUARIO_FINAL} caracteres)",
    )
    confirmar_password: str = Field(
        min_length=PASSWORD_MIN_LONGITUD_USUARIO_FINAL,
        description="Confirmacion de la nueva contrasena",
    )

    @field_validator("nueva_password")
    @classmethod
    def _validar_complejidad(cls, valor: str) -> str:
        if contar_tipos_caracter(valor) < PASSWORD_MIN_TIPOS_CARACTER:
            raise ValueError(
                f"La contrasena debe contener al menos {PASSWORD_MIN_TIPOS_CARACTER} de 4 tipos de "
                "caracter: minuscula, mayuscula, digito o caracter especial"
            )
        return valor

    @field_validator("nueva_password", mode="after")
    @classmethod
    def _validar_blacklist(cls, valor: str) -> str:
        if valor.lower().strip() in BLACKLIST_COMUNES:
            raise ValueError(
                "La contrasena es demasiado comun o conocida como insegura. "
                "Elige una contrasena unica que no aparezca en diccionarios conocidos."
            )
        return valor
