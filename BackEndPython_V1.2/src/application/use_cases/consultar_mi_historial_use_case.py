from __future__ import annotations

from src.domain.entities.registro_auditoria import RegistroAuditoria
from src.domain.ports.outbound.auditoria_lector_repository import AuditoriaLectorRepository
from src.domain.value_objects.filtro_auditoria import FiltroAuditoria
from src.domain.value_objects.pagina_auditoria import PaginaAuditoria


class ConsultarMiHistorialUseCase:
    """AP-0028: consulta paginada del historial de acciones del propio usuario.

    Recibe el user_id resuelto del token (nunca de un parametro) y delega en el lector,
    devolviendo la pagina de asientos junto con el total para la paginacion.
    """

    def __init__(self, lector: AuditoriaLectorRepository) -> None:
        self._lector: AuditoriaLectorRepository = lector

    async def ejecutar_async(self, user_id: int, filtro: FiltroAuditoria) -> PaginaAuditoria:
        items: list[RegistroAuditoria] = await self._lector.listar_por_usuario_async(
            user_id, filtro
        )
        total: int = await self._lector.contar_por_usuario_async(user_id, filtro)
        return PaginaAuditoria(
            items=items, page=filtro.page, page_size=filtro.page_size, total=total
        )
