from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EjecutivoFormDTO:
    """DTO para crear o actualizar un ejecutivo (tabla users_ejecutivos)."""
    tipo_documento: str
    numero_documento: str
    nombre_completo: str
    codigo_ejecutivo: str
    email: str
    celular: str
    perfil: str
    estado: bool
