from __future__ import annotations

from src.application.dto.banco_form_dto import BancoFormDTO
from src.application.dto.banco_list_dto import BancoListDTO
from src.application.dto.banco_list_item_dto import BancoListItemDTO
from src.domain.entities.banco_entity import BancoEntity
from src.domain.ports.outbound.banco_repository import BancoRepository


class GestionarBancosUseCase:
    """CRUD admin sobre dbo.bancos. Política 1C."""

    def __init__(self, banco_repo: BancoRepository) -> None:
        self._banco_repo: BancoRepository = banco_repo

    async def listar_async(
        self, page: int, page_size: int, nombre: str | None = None
    ) -> BancoListDTO:
        entities, total = await self._banco_repo.listar_paginado_async(
            page=page, page_size=page_size, nombre=nombre
        )
        items: list[BancoListItemDTO] = [
            BancoListItemDTO(tid=e.tid, nombre=e.nombre, codigo=e.codigo)
            for e in entities
        ]
        return BancoListDTO(items=items, total=total, page=page, page_size=page_size)

    async def obtener_async(self, tid: int) -> BancoEntity | None:
        return await self._banco_repo.obtener_por_id_async(tid)

    async def crear_async(self, dto: BancoFormDTO) -> BancoEntity:
        self._validar(dto)
        entity: BancoEntity = BancoEntity(
            tid=0,
            nombre=dto.nombre.strip(),
            codigo=(dto.codigo.strip() if dto.codigo else None),
        )
        return await self._banco_repo.crear_async(entity)

    async def actualizar_async(
        self, tid: int, dto: BancoFormDTO
    ) -> BancoEntity | None:
        self._validar(dto)
        entity: BancoEntity = BancoEntity(
            tid=tid,
            nombre=dto.nombre.strip(),
            codigo=(dto.codigo.strip() if dto.codigo else None),
        )
        return await self._banco_repo.actualizar_async(tid, entity)

    async def eliminar_async(self, tid: int) -> bool:
        if await self._banco_repo.existe_referenciado_async(tid):
            raise ValueError(
                "No se puede eliminar el banco porque está referenciado en perfiles de contacto"
            )
        return await self._banco_repo.eliminar_async(tid)

    @staticmethod
    def _validar(dto: BancoFormDTO) -> None:
        if not dto.nombre.strip():
            raise ValueError("El nombre del banco es obligatorio")
        if len(dto.nombre.strip()) > 200:
            raise ValueError("El nombre del banco no puede exceder 200 caracteres")
        if dto.codigo is not None and len(dto.codigo.strip()) > 10:
            raise ValueError("El código no puede exceder 10 caracteres")
