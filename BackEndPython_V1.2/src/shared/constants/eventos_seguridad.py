"""Constantes de eventos de auditoría de seguridad (AP-0022)."""
from typing import Final

# Tipos de evento
EVENTO_ACCESO: Final[str] = "acceso"
EVENTO_ACCESO_CONFIDENCIAL: Final[str] = "acceso_confidencial"
EVENTO_AUTENTICACION: Final[str] = "autenticacion"
EVENTO_AUTORIZACION: Final[str] = "autorizacion"
EVENTO_CAMBIO_CREDENCIAL: Final[str] = "cambio_credencial"
EVENTO_EXCEPCIONAL: Final[str] = "evento_excepcional"
# AP-0120: cambio de integridad de un archivo critico (File Integrity Monitoring).
EVENTO_INTEGRIDAD_ARCHIVO: Final[str] = "integridad_archivo"

# Resultado de la acción (éxito / fallo)
RESULTADO_EXITO: Final[str] = "exito"
RESULTADO_FALLO: Final[str] = "fallo"

# Nombre del logger dedicado de auditoría de seguridad
LOGGER_SEGURIDAD: Final[str] = "sufi.seguridad"

# Prefijos de ruta que exponen información confidencial (se marcan en el log).
RUTAS_CONFIDENCIALES: Final[tuple[str, ...]] = (
    "/api/v1/reportes",
    "/api/v1/documentos",
    "/api/v1/me/documentos",
    "/api/v1/me/perfil",
    "/api/v1/sapin",
    "/api/v1/admin",
)
