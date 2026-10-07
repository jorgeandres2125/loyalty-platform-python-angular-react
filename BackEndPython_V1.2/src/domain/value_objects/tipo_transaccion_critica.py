from enum import StrEnum


class TipoTransaccionCritica(StrEnum):
    """AP-0005: catalogo de transacciones criticas que exigen confirmacion OOB.

    Una operacion es critica cuando, ejecutada por un actor no legitimo, produce dano
    economico, perdida de control de acceso o un efecto dificil de revertir. El
    catalogo es la version MVP del motor de riesgo (clasificacion por tipo).
    """

    CAMBIO_CUENTA_BANCARIA = "cambio_cuenta_bancaria"
    CAMBIO_CORREO = "cambio_correo"
    ALTA_USUARIO_PRIVILEGIADO = "alta_usuario_privilegiado"
    CAMBIO_PERMISOS = "cambio_permisos"
    INACTIVACION_USUARIO = "inactivacion_usuario"
