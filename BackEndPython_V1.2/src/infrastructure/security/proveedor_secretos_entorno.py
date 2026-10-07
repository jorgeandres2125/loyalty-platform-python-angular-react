from __future__ import annotations


class ProveedorSecretosEntorno:
    """AP-0062: proveedor de secretos para dev y test. Devuelve los valores ya cargados por
    Settings desde las variables de entorno (inyectadas por Key Vault o Kubernetes en los
    entornos gestionados). Implementa ProveedorSecretos (PEP 544). No cachea: `invalidar` es
    no-op.
    """

    def __init__(self, valores: dict[str, str]) -> None:
        self._valores: dict[str, str] = dict(valores)

    def obtener(self, nombre: str) -> str | None:
        valor: str = self._valores.get(nombre, "")
        return valor or None

    def invalidar(self, nombre: str) -> None:
        return None
