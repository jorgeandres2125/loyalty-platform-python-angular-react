from __future__ import annotations

from src.application.services.servicio_ownership import ServicioOwnership
from src.domain.entities.desafio_oob import DesafioOob
from src.domain.ports.outbound.desafio_oob_store import DesafioOobStore
from src.domain.value_objects.resource_type import ResourceType


class OwnershipValidator:
    """AP-0055: verifica que el actor sea dueno de un objeto sensible.

    Centraliza la resolucion de propiedad por tipo de recurso: documentos y token
    SAPIN delegan en ServicioOwnership (uid contra numero_documento); el desafio OOB
    consulta el store y compara el titular. Deny-by-default: un tipo sin resolucion de
    propiedad devuelve False.
    """

    def __init__(
        self, servicio_ownership: ServicioOwnership, desafio_store: DesafioOobStore
    ) -> None:
        self._ownership: ServicioOwnership = servicio_ownership
        self._desafio_store: DesafioOobStore = desafio_store

    async def es_propietario(
        self, actor_uid: int, tipo: ResourceType, resource_id: str
    ) -> bool:
        if tipo in (ResourceType.DOCUMENTO, ResourceType.TOKEN_SAPIN):
            return await self._ownership.es_propietario_por_documento(
                actor_uid, resource_id
            )
        if tipo == ResourceType.DESAFIO_OOB:
            return await self._es_titular_desafio(actor_uid, resource_id)
        return False

    async def _es_titular_desafio(self, actor_uid: int, desafio_id: str) -> bool:
        desafio: DesafioOob | None = await self._desafio_store.obtener(desafio_id)
        if desafio is None:
            # No confirmado como ajeno: el caso de uso maneja la inexistencia (400),
            # preservando el mensaje de "desafio expirado". Aqui solo se deniega un
            # desafio que existe y pertenece a OTRO usuario.
            return True
        try:
            return int(desafio.uid) == actor_uid
        except (TypeError, ValueError):
            return False
