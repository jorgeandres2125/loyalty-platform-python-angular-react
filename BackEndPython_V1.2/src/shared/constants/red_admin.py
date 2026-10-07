"""Constantes de restriccion de acceso administrativo por red de gestion (AP-0052)."""
from typing import Final

# Cabecera anti-suplantacion: el edge (Ingress, API Gateway o WAF) la anade con un
# secreto compartido para probar que la IP de cliente reenviada es suya. Sin este
# secreto la app NO confia en las cabeceras de reenvio (el cliente podria
# falsificarlas) y usa la IP de la conexion directa.
HEADER_RED_ADMIN_EDGE_SECRET: Final[str] = "X-Edge-Red-Secret"

# Evento de auditoria del control (AP-0052 sobre el logger de AP-0022).
EVENTO_RED_ADMIN: Final[str] = "red_administrativa"

# Prefijos de ruta administrativos que SOLO deben ser alcanzables desde la red de
# gestion. Una peticion cuyo origen no pertenezca a ningun CIDR autorizado -> 403.
# Se excluye deliberadamente /api/v1/me y la subida propia de
# documentos del asesor final: aqui solo entran superficies inequivocamente
# administrativas.
RUTAS_ADMIN_RED: Final[tuple[str, ...]] = (
    "/api/v1/admin",
    "/api/v1/reportes",
)
