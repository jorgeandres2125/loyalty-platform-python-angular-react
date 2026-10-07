from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EjecutivoListItemDTO:
    id: int
    tipo_documento: str
    numero_documento: str
    nombre_completo: str
    codigo_ejecutivo: str
    celular: str
    email: str
    perfil: str
    perfil_nombre: str
    estado: bool
