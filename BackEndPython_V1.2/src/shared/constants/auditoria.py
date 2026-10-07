from __future__ import annotations

from typing import Final

# AP-0028: nombres de accion registrados en el historial de auditoria.
ACCION_LOGIN_EXITOSO: Final[str] = "LOGIN_EXITOSO"
ACCION_LOGIN_FALLIDO: Final[str] = "LOGIN_FALLIDO"
ACCION_PASSWORD_CAMBIADO: Final[str] = "PASSWORD_CAMBIADO"
# AP-0038: eventos del cambio autonomo de contrasena vencida y del enforcement en login.
ACCION_LOGIN_PASSWORD_EN_GRACIA: Final[str] = "LOGIN_PASSWORD_EN_GRACIA"
ACCION_LOGIN_RECHAZADO_PASSWORD_VENCIDO: Final[str] = "LOGIN_RECHAZADO_PASSWORD_VENCIDO"
ACCION_PASSWORD_CAMBIADO_EN_GRACIA: Final[str] = "PASSWORD_CAMBIADO_EN_GRACIA"
ACCION_PASSWORD_CAMBIO_DENEGADO_FUERA_GRACIA: Final[str] = "PASSWORD_CAMBIO_DENEGADO_FUERA_GRACIA"
# AP-0046, AP-0047 y AP-0048: eventos de contrasenas temporales.
ACCION_PASSWORD_TEMPORAL_EMITIDA: Final[str] = "PASSWORD_TEMPORAL_EMITIDA"
ACCION_LOGIN_PASSWORD_TEMPORAL: Final[str] = "LOGIN_PASSWORD_TEMPORAL"
ACCION_PASSWORD_TEMPORAL_RECHAZADA_VENCIDA: Final[str] = "PASSWORD_TEMPORAL_RECHAZADA_VENCIDA"
ACCION_PASSWORD_TEMPORAL_CONSUMIDA: Final[str] = "PASSWORD_TEMPORAL_CONSUMIDA"
ACCION_PERFIL_CONTACTO_ACTUALIZADO: Final[str] = "PERFIL_CONTACTO_ACTUALIZADO"
ACCION_PERFIL_TRIBUTARIO_ACTUALIZADO: Final[str] = "PERFIL_TRIBUTARIO_ACTUALIZADO"
ACCION_PERFIL_EMOCIONAL_ACTUALIZADO: Final[str] = "PERFIL_EMOCIONAL_ACTUALIZADO"
ACCION_DOCUMENTO_SUBIDO: Final[str] = "DOCUMENTO_SUBIDO"
ACCION_DOCUMENTO_ELIMINADO: Final[str] = "DOCUMENTO_ELIMINADO"
# AP-0049: eliminacion logica de cuentas con revocacion de sesiones.
ACCION_USUARIO_ELIMINADO: Final[str] = "USUARIO_ELIMINADO"

# Resultado del asiento.
RESULTADO_EXITO: Final[str] = "exito"
RESULTADO_FALLO: Final[str] = "fallo"

# Entidades afectadas (nombres de tabla del dominio).
ENTIDAD_PERFIL_CONTACTO: Final[str] = "users_perfil_contacto"
ENTIDAD_PERFIL_TRIBUTARIO: Final[str] = "users_perfil_tributario"
ENTIDAD_PERFIL_EMOCIONAL: Final[str] = "users_perfil_emocional"
ENTIDAD_DOCUMENTO: Final[str] = "user_documento"
ENTIDAD_SESION: Final[str] = "sesion"
ENTIDAD_PASSWORD_TEMPORAL: Final[str] = "user_password_temporal"

# Paginacion del historial.
HISTORIAL_PAGE_SIZE_DEFECTO: Final[int] = 20
HISTORIAL_PAGE_SIZE_MAX: Final[int] = 100

# AP-0028: roles autorizados a consultar el historial (todos los operativos; se excluyen
# los roles tecnicos anonimo y autenticado). Reflejan RolUsuario.
ROLES_HISTORIAL_PERMITIDOS: Final[frozenset[str]] = frozenset(
    {
        "administrator",
        "comisionista",
        "comisionista_consumo",
        "webmaster",
        "asesor_logistico",
        "asesor_comercial",
        "asesor_callcenter",
        "documentador",
        "asesor_consumo",
        "ejecutivo_consumo",
        "teleperformance",
        "ejecutivo_movilidad_consumo",
    }
)
