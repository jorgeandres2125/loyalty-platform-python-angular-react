from __future__ import annotations

from src.domain.entities.registro_auditoria import RegistroAuditoria
from src.domain.value_objects.filtro_auditoria import FiltroAuditoria


class InMemoryAuditoriaRepo:
    """AP-0028: adaptador en memoria del historial (escritor mas lector) para pruebas.

    Satisface AuditoriaEscritorGateway y AuditoriaLectorRepository (PEP 544). Guarda los
    asientos en una lista del proceso; util en pruebas y como fallback sin base de datos.
    """

    def __init__(self) -> None:
        self._registros: list[RegistroAuditoria] = []
        self._secuencia: int = 0

    async def guardar_async(self, registro: RegistroAuditoria) -> None:
        self._secuencia += 1
        registro.id = self._secuencia
        self._registros.append(registro)

    async def listar_por_usuario_async(
        self, user_id: int, filtro: FiltroAuditoria
    ) -> list[RegistroAuditoria]:
        filtrados: list[RegistroAuditoria] = self._filtrar(user_id, filtro)
        filtrados.sort(key=lambda reg: reg.creado_iso, reverse=True)
        return filtrados[filtro.offset : filtro.offset + filtro.limit]

    async def contar_por_usuario_async(self, user_id: int, filtro: FiltroAuditoria) -> int:
        return len(self._filtrar(user_id, filtro))

    def _filtrar(self, user_id: int, filtro: FiltroAuditoria) -> list[RegistroAuditoria]:
        resultado: list[RegistroAuditoria] = [
            reg for reg in self._registros if reg.user_id == user_id
        ]
        if filtro.accion:
            resultado = [reg for reg in resultado if reg.accion == filtro.accion]
        if filtro.desde_iso:
            resultado = [reg for reg in resultado if reg.creado_iso >= filtro.desde_iso]
        if filtro.hasta_iso:
            resultado = [reg for reg in resultado if reg.creado_iso <= filtro.hasta_iso]
        return resultado
