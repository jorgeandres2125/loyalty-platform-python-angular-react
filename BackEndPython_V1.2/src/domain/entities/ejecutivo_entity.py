from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EjecutivoEntity:
    """Ejecutivo operacional — tabla users_ejecutivos."""
    numero_documento: str = ""
    nombre_completo: str = ""
    tipo_documento: str = ""
    codigo_ejecutivo: str = ""
    celular: str = ""
    perfil: str = ""
    email: str = ""
    estado: bool = True
    id: int | None = None
