from __future__ import annotations

from sqlalchemy import URL

from src.domain.exceptions.secreto_no_disponible import SecretoNoDisponible
from src.domain.ports.outbound.proveedor_secretos import ProveedorSecretos
from src.shared.constants.secretos import PROVEEDOR_SECRETOS_PAM


class ResolvedorCredencialBd:
    """AP-0062: resuelve la URL de conexion a la BD.

    En modo distinto de PAM devuelve la URL directa (comportamiento actual, sin cambios). En
    modo PAM obtiene usuario y contrasena del proveedor de secretos (broker PAM) en cada
    resolucion, tolerando rotacion; `invalidar` fuerza el re-fetch tras un fallo de auth para
    reconstruir la conexion con la credencial rotada, sin redeploy.
    """

    def __init__(
        self,
        modo: str,
        url_directa: str,
        proveedor: ProveedorSecretos,
        host: str,
        port: int,
        database: str,
        driver: str,
        nombre_usuario: str,
        nombre_password: str,
    ) -> None:
        self._modo: str = modo
        self._url_directa: str = url_directa
        self._proveedor: ProveedorSecretos = proveedor
        self._host: str = host
        self._port: int = port
        self._database: str = database
        self._driver: str = driver
        self._nombre_usuario: str = nombre_usuario
        self._nombre_password: str = nombre_password

    def url(self) -> str:
        if self._modo != PROVEEDOR_SECRETOS_PAM:
            return self._url_directa
        usuario: str | None = self._proveedor.obtener(self._nombre_usuario)
        password: str | None = self._proveedor.obtener(self._nombre_password)
        if not usuario or not password:
            raise SecretoNoDisponible(
                "AP-0062: credencial de BD no disponible en el proveedor PAM"
            )
        objeto: URL = URL.create(
            "mssql+aioodbc",
            username=usuario,
            password=password,
            host=self._host,
            port=self._port,
            database=self._database,
            query={"driver": self._driver, "TrustServerCertificate": "yes"},
        )
        return objeto.render_as_string(hide_password=False)

    def invalidar(self) -> None:
        self._proveedor.invalidar(self._nombre_usuario)
        self._proveedor.invalidar(self._nombre_password)
