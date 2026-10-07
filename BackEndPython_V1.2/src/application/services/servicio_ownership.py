from __future__ import annotations

from src.domain.entities.usuario_entity import UsuarioEntity
from src.domain.ports.outbound.usuario_repository import UsuarioRepository


class ServicioOwnership:
    """AP-0053/AP-0055: primitiva de verificacion de propiedad por numero_documento.

    El JWT lleva sub=uid; los documentos, perfiles y tokens SAPIN se llavean por
    numero_documento (cedula). Resuelve el numero_documento propio del actor
    (uid a dbo.users.name, la misma via que MiPerfilUseCase) y lo compara con el del
    recurso. La usa OwnershipValidator (AP-0055) como resolucion de propiedad para los
    tipos de objeto llaveados por numero_documento. Deny-by-default: si no se puede
    confirmar la propiedad, es False.
    """

    def __init__(self, usuario_repo: UsuarioRepository) -> None:
        self._usuario_repo: UsuarioRepository = usuario_repo

    async def es_propietario_por_documento(
        self, actor_uid: int, numero_documento: str
    ) -> bool:
        """True si el numero_documento pertenece al actor (comparacion exacta)."""
        usuario: UsuarioEntity | None = await self._usuario_repo.obtener_por_uid_async(
            actor_uid
        )
        propio: str | None = usuario.nombre if usuario is not None else None
        return bool(propio) and propio == numero_documento
