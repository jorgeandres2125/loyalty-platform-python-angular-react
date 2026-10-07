from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OficinaEntity:
    """Oficina comercial — tabla oficinas. cpid = ciudades.cid."""
    cod_oficinas: int | None = None
    id_oficinas: int | None = None
    nom_oficinas: str = ""
    marca: str = ""
    regional: str = ""
    cpid: int | None = None       # FK → ciudades.cid
    ind_activo: bool | None = None
    # Enriquecido via JOIN (solo lectura, no se persiste)
    ciudad_nombre: str = ""
    did: int | None = None        # ciudades.did → departamentos.did
    departamento_nombre: str = ""
    # Relación N:M via canales_oficinas
    canales_ids: list[int] = field(default_factory=list)
