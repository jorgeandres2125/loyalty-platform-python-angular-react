from __future__ import annotations

from typing import Final

from src.application.services.auditor_acceso_objeto import AuditorAccesoObjeto
from src.application.services.ownership_validator import OwnershipValidator
from src.application.services.permission_evaluator import PermissionEvaluator
from src.domain.value_objects.accion_recurso import AccionRecurso
from src.domain.value_objects.decision_acceso import DecisionAcceso
from src.domain.value_objects.permiso import Permiso
from src.domain.value_objects.regla_acceso import ReglaAcceso
from src.domain.value_objects.resource_type import ResourceType
from src.domain.value_objects.rol_usuario import RolUsuario
from src.shared.constants.politica_acceso import POLITICA_ACCESO
from src.shared.constants.rbac import permisos_de_roles

MODO_ENFORCE: Final[str] = "enforce"
MODO_AUDIT: Final[str] = "audit"
MODO_OFF: Final[str] = "off"

_MENSAJE: Final[dict[int, str]] = {
    403: "No autorizado para este recurso",
    404: "Recurso no encontrado",
}


class AuthorizationService:
    """AP-0055: punto unico de autorizacion a nivel de objeto. Orquesta RBAC (rol),
    ownership (propiedad del objeto) y auditoria segun la politica declarativa. El
    modo (enforce, audit u off) permite despliegue progresivo: en audit registra la
    denegacion pero deja pasar (canary)."""

    def __init__(
        self,
        permission_evaluator: PermissionEvaluator,
        ownership_validator: OwnershipValidator,
        auditor: AuditorAccesoObjeto,
        modo: str,
    ) -> None:
        self._permisos: PermissionEvaluator = permission_evaluator
        self._ownership: OwnershipValidator = ownership_validator
        self._auditor: AuditorAccesoObjeto = auditor
        self._modo: str = modo

    async def autorizar(
        self,
        actor_uid: int,
        roles: frozenset[RolUsuario],
        tipo: ResourceType,
        accion: AccionRecurso,
        resource_id: str | None,
    ) -> DecisionAcceso:
        if self._modo == MODO_OFF:
            return DecisionAcceso(permitido=True)
        regla: ReglaAcceso | None = POLITICA_ACCESO.get((tipo, accion))
        if regla is None:
            return await self._resolver(
                actor_uid, tipo, resource_id, accion, False, "sin-politica", 403
            )
        efectivos: frozenset[Permiso] = permisos_de_roles(roles)
        if not self._permisos.permite_rol(efectivos, regla):
            return await self._resolver(actor_uid, tipo, resource_id, accion, False, "rol", 403)
        es_staff: bool = self._permisos.es_staff(efectivos, regla)
        if regla.ownership_required and not es_staff:
            propio: bool = resource_id is not None and await self._ownership.es_propietario(
                actor_uid, tipo, resource_id
            )
            if not propio:
                return await self._resolver(
                    actor_uid, tipo, resource_id, accion, False, "ownership", regla.deny_status
                )
        return await self._resolver(actor_uid, tipo, resource_id, accion, True, "", 200)

    async def _resolver(
        self,
        actor_uid: int,
        tipo: ResourceType,
        resource_id: str | None,
        accion: AccionRecurso,
        permitido: bool,
        motivo: str,
        status: int,
    ) -> DecisionAcceso:
        await self._auditor.registrar(
            actor_uid, tipo, resource_id, accion, permitido, motivo, self._modo
        )
        if permitido:
            return DecisionAcceso(permitido=True)
        if self._modo == MODO_AUDIT:
            return DecisionAcceso(permitido=True, motivo=motivo)
        return DecisionAcceso(
            permitido=False,
            status=status,
            mensaje=_MENSAJE.get(status, "No autorizado"),
            motivo=motivo,
        )
