from enum import StrEnum


class Permiso(StrEnum):
    """Permisos canonicos de autorizacion del stack SUFI (AP-0053).

    Vocabulario unico del RBAC por endpoint, reconciliado con el catalogo de
    autorizacion de negocio (spec 17). Los permisos "_PROPIO" se combinan siempre
    con verificacion de ownership; los de gestion ("_GESTIONAR", "_MODERAR",
    "_EXPORTAR", "_AUTORIZAR") son de staff o administracion y no dependen de
    propiedad. Deny-by-default: un endpoint sin permiso declarado no se sirve.
    """

    # Administracion y panel de control
    ADMIN_CATALOGOS_GESTIONAR = "admin_catalogos_gestionar"
    USUARIOS_GESTIONAR_ESTADO = "usuarios_gestionar_estado"
    COMISIONISTAS_GESTIONAR_ESTADO = "comisionistas_gestionar_estado"
    AUTORIZACIONES_GESTIONAR = "autorizaciones_gestionar"
    ASIGNACIONES_GESTIONAR = "asignaciones_gestionar"
    INACTIVACION_AUTORIZAR = "inactivacion_autorizar"

    # Gestion de asesores y operaciones de staff
    MOVILIDAD_ASESORES_GESTIONAR = "movilidad_asesores_gestionar"
    CONSUMO_ASESORES_GESTIONAR = "consumo_asesores_gestionar"
    DOCUMENTOS_MODERAR = "documentos_moderar"
    REPORTES_EXPORTAR = "reportes_exportar"
    INCENTIVOS_GESTIONAR = "incentivos_gestionar"

    # Recursos propios (usuario final; exigen ownership)
    MOVILIDAD_PERFIL_VER_PROPIO = "movilidad_perfil_ver_propio"
    CONSUMO_PERFIL_VER_PROPIO = "consumo_perfil_ver_propio"
    DOCUMENTOS_SUBIR_PROPIO = "documentos_subir_propio"
    DISPOSITIVOS_VER_PROPIO = "dispositivos_ver_propio"
    AUDITORIA_VER_PROPIO = "auditoria_ver_propio"

    # Consulta de catalogos de referencia (baja sensibilidad)
    CATALOGOS_REFERENCIA_VER = "catalogos_referencia_ver"
    # AP-0060: administracion (escritura) de catalogos de referencia -- canales,
    # oficinas, ejecutivos. Distinto de _VER (lectura, otorgado a todo rol
    # autenticado incluidos comisionistas); _GESTIONAR es exclusivo de staff y
    # administracion.
    CATALOGOS_REFERENCIA_GESTIONAR = "catalogos_referencia_gestionar"

    # Transacciones sensibles
    FIRMA_GESTIONAR = "firma_gestionar"
    OOB_AUTORIZAR = "oob_autorizar"

    # AP-0157: gestion de bloqueos de cuenta. Suave (temporal/operativo) y duro
    # (administrativo/seguridad); el duro exige permiso propio y remocion privilegiada.
    USUARIOS_SOFTLOCK_GESTIONAR = "usuarios_softlock_gestionar"
    USUARIOS_HARDLOCK_GESTIONAR = "usuarios_hardlock_gestionar"
