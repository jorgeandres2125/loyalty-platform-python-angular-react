"""Constantes de autenticacion mutua TLS por certificado de cliente (AP-0003)."""
from typing import Final

# Cabeceras de confianza que el edge (Ingress o API Gateway) inyecta tras validar
# el certificado de cliente en el handshake mTLS. La app NO termina TLS: consume la
# identidad ya verificada. El edge DEBE sobrescribir estas cabeceras en cada
# peticion (y el cliente no puede fijarlas) para evitar suplantacion.
HEADER_CLIENT_CERT_FINGERPRINT: Final[str] = "X-Client-Cert-Fingerprint"
HEADER_CLIENT_CERT_SUBJECT: Final[str] = "X-Client-Cert-Subject"
HEADER_CLIENT_CERT_SERIAL: Final[str] = "X-Client-Cert-Serial"

# Secreto anti-suplantacion: el edge anade esta cabecera con un valor compartido
# que solo el conoce; la app rechaza cabeceras de identidad que no lo acompanen.
HEADER_MTLS_EDGE_SECRET: Final[str] = "X-Edge-Mtls-Secret"

# Evento de auditoria del control mTLS (AP-0003 sobre el logger de AP-0022).
EVENTO_MTLS: Final[str] = "mtls_certificado_cliente"

# Prefijos de ruta que EXIGEN certificado de cliente (canales criticos M2M y admin).
# Peticion sin certificado valido y mapeado a estas rutas -> 403.
RUTAS_MTLS_OBLIGATORIO: Final[tuple[str, ...]] = (
    "/api/v1/sapin",
    "/api/v1/reportes",
    "/api/v1/admin",
)
