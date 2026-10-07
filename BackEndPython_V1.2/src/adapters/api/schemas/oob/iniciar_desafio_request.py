from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.domain.value_objects.tipo_transaccion_critica import TipoTransaccionCritica


class IniciarDesafioRequest(BaseModel):
    """AP-0005: inicia la confirmacion OOB de una transaccion critica."""

    model_config = ConfigDict(extra="forbid")

    tipo_transaccion: TipoTransaccionCritica
    payload: dict[str, object] = Field(
        default_factory=dict,
        description="Datos de la operacion; ligan el desafio por su hash.",
    )
