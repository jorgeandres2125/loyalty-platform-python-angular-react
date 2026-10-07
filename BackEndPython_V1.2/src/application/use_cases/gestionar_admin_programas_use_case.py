from __future__ import annotations

from src.application.dto.admin_programa_form_dto import AdminProgramaFormDTO
from src.domain.entities.comisionista_programa_entity import (
    ComisionistaProgramaEntity,
)
from src.domain.ports.outbound.admin_programa_repository import AdminProgramaRepository


class GestionarAdminProgramasUseCase:
    """Edición administrativa de dbo.comisionistas_programa (solo nombre)."""

    def __init__(self, programa_repo: AdminProgramaRepository) -> None:
        self._programa_repo: AdminProgramaRepository = programa_repo

    async def listar_async(self) -> list[ComisionistaProgramaEntity]:
        return await self._programa_repo.listar_async()

    async def obtener_async(self, cpid: int) -> ComisionistaProgramaEntity | None:
        return await self._programa_repo.obtener_por_id_async(cpid)

    async def actualizar_nombre_async(
        self, cpid: int, dto: AdminProgramaFormDTO
    ) -> ComisionistaProgramaEntity | None:
        self._validar(dto)
        return await self._programa_repo.actualizar_nombre_async(
            cpid, dto.cp_nombre.strip()
        )

    @staticmethod
    def _validar(dto: AdminProgramaFormDTO) -> None:
        if not dto.cp_nombre.strip():
            raise ValueError("El nombre del programa es obligatorio")
        if len(dto.cp_nombre.strip()) > 50:
            raise ValueError("El nombre del programa no puede exceder 50 caracteres")
