from __future__ import annotations

from enum import StrEnum


class OrigenPasswordTemporal(StrEnum):
    """AP-0047: quien genero la contrasena temporal (origen de la credencial).

    - ADMIN: administrador del portal desde el Panel de Control.
    - SOPORTE: operador de soporte autorizado.
    - SISTEMA: provision automatica (reservado para la creacion de usuarios).
    """

    ADMIN = "admin"
    SOPORTE = "soporte"
    SISTEMA = "sistema"
