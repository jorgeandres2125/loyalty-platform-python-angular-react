"""Constantes del subsistema de confirmacion fuera de banda (OOB) â€” AP-0005."""
from typing import Final

from src.shared.constants.otp import validar_longitud_otp

# Longitud del codigo OOB (6 digitos; TTL corto y un solo uso). AP-0135: piso 6 por codigo.
OOB_CODIGO_LONGITUD: Final[int] = validar_longitud_otp(6, "OOB_CODIGO_LONGITUD")

# Asunto del correo del desafio OOB.
OOB_ASUNTO: Final[str] = "Confirma tu operacion â€” SUFI Siempre a tu lado"

# Evento de auditoria del subsistema OOB (sobre el logger de seguridad de AP-0022).
EVENTO_OOB: Final[str] = "confirmacion_oob"

# Descripcion legible por tipo de transaccion critica (para el cuerpo del correo).
DESCRIPCION_TRANSACCION: Final[dict[str, str]] = {
    "cambio_cuenta_bancaria": "un cambio de cuenta bancaria",
    "cambio_correo": "un cambio de correo electronico",
    "alta_usuario_privilegiado": "el alta de un usuario privilegiado",
    "cambio_permisos": "un cambio de permisos",
    "inactivacion_usuario": "la inactivacion de un usuario",
}
