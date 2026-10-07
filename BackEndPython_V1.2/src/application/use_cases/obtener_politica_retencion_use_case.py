from __future__ import annotations

from src.domain.services.clasificador_retencion import ClasificadorRetencion
from src.domain.value_objects.item_politica_retencion import ItemPoliticaRetencion
from src.shared.constants.retencion_log import BASE_REGULATORIA


class ObtenerPoliticaRetencionUseCase:
    """AP-0026: devuelve la politica de retencion vigente como evidencia de auditoria.

    Enumera cada categoria con su plazo en dias (configurado por entorno) y la base
    regulatoria que lo sustenta, para que un auditor verifique la retencion declarada sin
    acceso al codigo.
    """

    def __init__(self, clasificador: ClasificadorRetencion) -> None:
        self._clasificador: ClasificadorRetencion = clasificador

    def ejecutar(self) -> list[ItemPoliticaRetencion]:
        items: list[ItemPoliticaRetencion] = []
        for categoria, dias in self._clasificador.dias_por_categoria.items():
            base: str = BASE_REGULATORIA.get(categoria.value, "")
            items.append(
                ItemPoliticaRetencion(categoria=categoria, dias=dias, base_regulatoria=base)
            )
        return items
