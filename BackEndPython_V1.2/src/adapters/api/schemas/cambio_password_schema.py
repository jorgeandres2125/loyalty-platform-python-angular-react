from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.shared.constants.password_blacklist import BLACKLIST_COMUNES
from src.shared.constants.password_policy import (
    PASSWORD_MIN_LONGITUD_USUARIO_FINAL,
    PASSWORD_MIN_TIPOS_CARACTER,
    contar_tipos_caracter,
)


class CambioPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # AP-0020: re-autenticacion fuerte. min_length=1 para soportar claves legacy.
    password_actual: str = Field(min_length=1, description="Contrasena actual (re-autenticacion)")
    # AP-0044: minimo 12 caracteres al establecer la clave.
    nueva_password: str = Field(
        min_length=PASSWORD_MIN_LONGITUD_USUARIO_FINAL,
        description=f"Nueva contrasena (minimo {PASSWORD_MIN_LONGITUD_USUARIO_FINAL} caracteres)",
    )
    confirmar_password: str = Field(
        min_length=PASSWORD_MIN_LONGITUD_USUARIO_FINAL,
        description="Confirmacion de la nueva contrasena",
    )

    # AP-0051: complejidad — minimo 3 de los 4 tipos de caracter.
    @field_validator("nueva_password")
    @classmethod
    def _validar_complejidad(cls, valor: str) -> str:
        if contar_tipos_caracter(valor) < PASSWORD_MIN_TIPOS_CARACTER:
            raise ValueError(
                f"La contrasena debe contener al menos {PASSWORD_MIN_TIPOS_CARACTER} de 4 tipos de "
                "caracter: minuscula, mayuscula, digito o caracter especial"
            )
        return valor

    # AP-0159: blacklist estatica — la contrasena no puede ser un valor conocido como inseguro.
    # La validacion contextual (contrasena != nombre de usuario) se aplica en la capa de servicio
    # donde se dispone de los datos del usuario autenticado.
    @field_validator("nueva_password", mode="after")
    @classmethod
    def _validar_blacklist(cls, valor: str) -> str:
        if valor.lower().strip() in BLACKLIST_COMUNES:
            raise ValueError(
                "La contrasena es demasiado comun o conocida como insegura. "
                "Elige una contrasena unica que no aparezca en diccionarios conocidos."
            )
        return valor
