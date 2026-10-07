"""AP-0055: politica declarativa de acceso a objetos sensibles (fuente unica)."""
from typing import Final

from src.domain.value_objects.accion_recurso import AccionRecurso
from src.domain.value_objects.permiso import Permiso
from src.domain.value_objects.regla_acceso import ReglaAcceso
from src.domain.value_objects.resource_type import ResourceType

POLITICA_ACCESO: Final[dict[tuple[ResourceType, AccionRecurso], ReglaAcceso]] = {
    # Documentos: el comisionista sube el suyo; el staff (moderador) opera sobre
    # cualquiera (bypass de propiedad).
    (ResourceType.DOCUMENTO, AccionRecurso.CREATE): ReglaAcceso(
        permisos=frozenset({Permiso.DOCUMENTOS_SUBIR_PROPIO}),
        staff_bypass=frozenset({Permiso.DOCUMENTOS_MODERAR}),
        ownership_required=True,
        deny_status=403,
    ),
    # Token SAPIN de incentivos: estrictamente personal, sin bypass de staff.
    (ResourceType.TOKEN_SAPIN, AccionRecurso.CREATE): ReglaAcceso(
        permisos=frozenset(
            {Permiso.MOVILIDAD_PERFIL_VER_PROPIO, Permiso.CONSUMO_PERFIL_VER_PROPIO}
        ),
        ownership_required=True,
        deny_status=403,
    ),
    # Desafio OOB: solo el titular puede resolverlo. 404 oculta la existencia del
    # desafio de un tercero (AP-0055).
    (ResourceType.DESAFIO_OOB, AccionRecurso.RESOLVE): ReglaAcceso(
        permisos=frozenset({Permiso.OOB_AUTORIZAR}),
        ownership_required=True,
        deny_status=404,
    ),
    # Firma digital: autoservicio (el emisor es siempre el propio actor); no hay
    # objeto de un tercero que proteger, solo control de rol y auditoria.
    (ResourceType.EVIDENCIA_FIRMA, AccionRecurso.CREATE): ReglaAcceso(
        ownership_required=False,
        deny_status=403,
    ),
    # AP-0055 M3: operaciones de staff sobre documentos de CUALQUIER asesor. El rol
    # DOCUMENTOS_MODERAR autoriza sobre todos los objetos (ownership no aplica); el
    # valor de M3 es dejar traza por-objeto de cada acceso (quien, que documento, que
    # accion) via AuditorAccesoObjeto.
    (ResourceType.DOCUMENTO, AccionRecurso.READ): ReglaAcceso(
        permisos=frozenset({Permiso.DOCUMENTOS_MODERAR}),
        deny_status=403,
    ),
    (ResourceType.DOCUMENTO, AccionRecurso.UPDATE): ReglaAcceso(
        permisos=frozenset({Permiso.DOCUMENTOS_MODERAR}),
        deny_status=403,
    ),
    (ResourceType.DOCUMENTO, AccionRecurso.DELETE): ReglaAcceso(
        permisos=frozenset({Permiso.DOCUMENTOS_MODERAR}),
        deny_status=403,
    ),
    (ResourceType.DOCUMENTO, AccionRecurso.DOWNLOAD): ReglaAcceso(
        permisos=frozenset({Permiso.DOCUMENTOS_MODERAR}),
        deny_status=403,
    ),
    (ResourceType.DOCUMENTO, AccionRecurso.APPROVE): ReglaAcceso(
        permisos=frozenset({Permiso.DOCUMENTOS_MODERAR}),
        deny_status=403,
    ),
}
