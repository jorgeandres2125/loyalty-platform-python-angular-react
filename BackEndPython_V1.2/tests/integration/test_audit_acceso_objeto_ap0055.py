from __future__ import annotations

from src.application.services.auditor_acceso_objeto import AuditorAccesoObjeto
from src.application.services.servicio_auditoria import ServicioAuditoria
from src.domain.value_objects.accion_recurso import AccionRecurso
from src.domain.value_objects.filtro_auditoria import FiltroAuditoria
from src.domain.value_objects.resource_type import ResourceType
from src.infrastructure.external.in_memory_auditoria_repo import InMemoryAuditoriaRepo

_FILTRO = FiltroAuditoria(page=1, page_size=10)


class TestTrazabilidadAccesoObjeto:
    """AP-0055 M6 (seccion 6): cada decision de acceso a objeto (ALLOW o DENY) se
    persiste en audit_log (AP-0028) y es recuperable por el propio usuario, con actor,
    recurso, accion y resultado."""

    async def test_allow_persiste_registro_recuperable(self) -> None:
        repo = InMemoryAuditoriaRepo()
        auditor = AuditorAccesoObjeto(servicio_auditoria=ServicioAuditoria(escritor=repo))
        await auditor.registrar(
            actor_uid=7,
            tipo=ResourceType.DOCUMENTO,
            resource_id="123456",
            accion=AccionRecurso.READ,
            permitido=True,
            motivo="",
            modo="enforce",
        )
        regs = await repo.listar_por_usuario_async(7, _FILTRO)
        assert len(regs) == 1
        assert regs[0].accion == "acceso_objeto"
        assert regs[0].entidad == "documento"
        assert regs[0].entidad_id == "123456"
        assert regs[0].resultado == "exito"
        assert regs[0].detalle is not None
        assert "read" in regs[0].detalle

    async def test_deny_persiste_como_fallo_con_motivo(self) -> None:
        repo = InMemoryAuditoriaRepo()
        auditor = AuditorAccesoObjeto(servicio_auditoria=ServicioAuditoria(escritor=repo))
        await auditor.registrar(
            actor_uid=9,
            tipo=ResourceType.TOKEN_SAPIN,
            resource_id="999999",
            accion=AccionRecurso.CREATE,
            permitido=False,
            motivo="ownership",
            modo="enforce",
        )
        regs = await repo.listar_por_usuario_async(9, _FILTRO)
        assert len(regs) == 1
        assert regs[0].resultado == "fallo"
        assert regs[0].detalle is not None
        assert "ownership" in regs[0].detalle

    async def test_cada_usuario_solo_ve_lo_suyo(self) -> None:
        repo = InMemoryAuditoriaRepo()
        auditor = AuditorAccesoObjeto(servicio_auditoria=ServicioAuditoria(escritor=repo))
        await auditor.registrar(
            actor_uid=1,
            tipo=ResourceType.DOCUMENTO,
            resource_id="a",
            accion=AccionRecurso.READ,
            permitido=True,
            motivo="",
            modo="enforce",
        )
        await auditor.registrar(
            actor_uid=2,
            tipo=ResourceType.DOCUMENTO,
            resource_id="b",
            accion=AccionRecurso.DELETE,
            permitido=True,
            motivo="",
            modo="enforce",
        )
        assert len(await repo.listar_por_usuario_async(1, _FILTRO)) == 1
        assert len(await repo.listar_por_usuario_async(2, _FILTRO)) == 1
