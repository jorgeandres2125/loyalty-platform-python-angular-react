from enum import Enum


class MotivoCierreSesion(str, Enum):
    """AP-0132: causa por la que una sesion del Session Registry deja de estar activa.

    Se registra junto con la fecha de cierre para dejar evidencia auditable (AP-0022,
    AP-0028) de por que y cuando termino cada sesion, tanto en cierres manuales como
    automaticos."""

    LOGOUT = "logout"
    EXPIRACION = "expiracion"
    INACTIVIDAD = "inactividad"
    REVOCACION_ADMIN = "revocacion_admin"
    LIMITE_CONCURRENCIA = "limite_concurrencia"
    CAMBIO_CREDENCIAL = "cambio_credencial"
