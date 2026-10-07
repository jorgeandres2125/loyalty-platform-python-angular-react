from __future__ import annotations

from src.application.dto.afp_form_dto import AfpFormDTO
from src.application.dto.afp_list_dto import AfpListDTO
from src.application.dto.afp_list_item_dto import AfpListItemDTO
from src.domain.entities.afp_entity import AfpEntity
from src.domain.ports.outbound.afp_repository import AfpRepository


class GestionarAfpUseCase:
    """Caso de uso administrativo: CRUD sobre el catálogo dbo.afp.

    Política de delete (1C): hard delete con guardia de integridad referencial.
    Si la AFP está usada por algún perfil tributario, se rechaza con ValueError
    (el router lo convierte en HTTP 409 Conflict).
    """

    def __init__(self, afp_repo: AfpRepository) -> None:
        self._afp_repo: AfpRepository = afp_repo

    async def listar_async(
        self,
        page: int,
        page_size: int,
        nombre: str | None = None,
    ) -> AfpListDTO:
        entities, total = await self._afp_repo.listar_paginado_async(
            page=page,
            page_size=page_size,
            nombre=nombre,
        )
        items: list[AfpListItemDTO] = [
            AfpListItemDTO(tid=entity.tid, nombre=entity.nombre, nit=entity.nit)
            for entity in entities
        ]
        return AfpListDTO(items=items, total=total, page=page, page_size=page_size)

    async def obtener_async(self, tid: int) -> AfpEntity | None:
        return await self._afp_repo.obtener_por_id_async(tid)

    async def crear_async(self, dto: AfpFormDTO) -> AfpEntity:
        self._validar(dto)
        entity: AfpEntity = AfpEntity(
            tid=0,
            nombre=dto.nombre.strip(),
            nit=(dto.nit.strip() if dto.nit else None),
        )
        return await self._afp_repo.crear_async(entity)

    async def actualizar_async(
        self, tid: int, dto: AfpFormDTO
    ) -> AfpEntity | None:
        self._validar(dto)
        entity: AfpEntity = AfpEntity(
            tid=tid,
            nombre=dto.nombre.strip(),
            nit=(dto.nit.strip() if dto.nit else None),
        )
        return await self._afp_repo.actualizar_async(tid, entity)

    async def eliminar_async(self, tid: int) -> bool:
        if await self._afp_repo.existe_referenciado_async(tid):
            raise ValueError(
                "No se puede eliminar la AFP porque está referenciada en perfiles tributarios"
            )
        return await self._afp_repo.eliminar_async(tid)

    @staticmethod
    def _validar(dto: AfpFormDTO) -> None:
        if not dto.nombre.strip():
            raise ValueError("El nombre de la AFP es obligatorio")
        if len(dto.nombre.strip()) > 200:
            raise ValueError("El nombre de la AFP no puede exceder 200 caracteres")
        if dto.nit is not None and len(dto.nit.strip()) > 30:
            raise ValueError("El NIT no puede exceder 30 caracteres")
