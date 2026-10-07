from __future__ import annotations

from typing import Protocol


class ProveedorClaveOidc(Protocol):
    """AP-0010: proveedor de la clave de firma OIDC (JWS asimetrico) y su JWKS.

    Contrato estructural (PEP 544). Firma tokens estandar con un algoritmo asimetrico
    (ES256 por defecto) cuya clave privada no se expone; publica la clave publica como
    JWKS para que cualquier Relying Party valide de forma independiente. En produccion
    la clave se custodia en KMS o HSM (AP-0180); en desarrollo se carga de settings o
    se genera efimera.
    """

    kid: str
    algoritmo: str

    def firmar(self, claims: dict[str, object]) -> str: ...
    def clave_publica_pem(self) -> str: ...
    def jwks(self) -> dict[str, object]: ...
