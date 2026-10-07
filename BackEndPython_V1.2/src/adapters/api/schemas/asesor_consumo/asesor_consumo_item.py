from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from src.adapters.api.schemas.asesor_consumo.canales_item import CanalesItem
from src.adapters.api.schemas.asesor_consumo.oficina_item import OficinaItem
from src.adapters.api.schemas.asesor_consumo.subprograma_item import SubprogramaItem
from src.adapters.api.schemas.shared.ciudad_item import CiudadItem
from src.adapters.api.schemas.shared.departamento_item import DepartamentoItem
from src.adapters.api.schemas.shared.genero_item import GeneroItem
from src.adapters.api.schemas.shared.programa_item import ProgramaItem
from src.adapters.api.schemas.shared.tipo_documento_item import TipoDocumentoItem


class AsesorConsumoItem(BaseModel):
    """Fila de la lista paginada — tabla users_perfil_contacto (programa Consumo)."""

    numero_documento: str
    nombre_completo: str | None = None
    tipo_documento: TipoDocumentoItem | None = None
    genero: GeneroItem | None = None
    celular: str | None = None
    canal: CanalesItem | None = None
    oficina: OficinaItem | None = None
    programa: ProgramaItem | None = None
    subprograma: SubprogramaItem | None = None
    departamento: DepartamentoItem | None = None
    ciudad: CiudadItem | None = None
    estado: int | None = None
    fecha_completado: date | None = None
    incentivos: bool | None = None
    email: str | None = None
