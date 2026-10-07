from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class EjecutivoCatalogoEntity:
    """Tabla Ejecutivos (capital E) — importación legacy del mainframe."""
    usuario_asesor: str = ""
    email_asesor: str = ""
    usuario_comisionista: str = ""
    email_comisionista: str = ""
    nombre_comisionista: str = ""
    fecha_registro: datetime | None = None
