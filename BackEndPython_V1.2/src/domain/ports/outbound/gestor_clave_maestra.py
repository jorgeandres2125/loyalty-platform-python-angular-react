from __future__ import annotations

from typing import Protocol


class GestorClaveMaestra(Protocol):
    """Puerto de salida para el sistema que custodia la clave maestra (KEK) sin
    exponerla durante su uso (AP-0180: HSM o KMS).

    El KEK nunca sale del proveedor: la aplicacion envia material de clave (DEK)
    para envolver o desenvolver y recibe solo el resultado. En produccion lo
    implementa un KMS o HSM real (AWS KMS, Azure Key Vault, HSM); en desarrollo
    un sustituto de software equivalente en interfaz.
    """

    @property
    def respaldado_por_hsm(self) -> bool:
        """True si el KEK reside en un HSM o KMS y no se expone al proceso."""
        ...

    def cifrar_clave_datos(self, clave_datos: bytes) -> bytes:
        """Envuelve (cifra) una clave de datos (DEK) con el KEK custodiado."""
        ...

    def descifrar_clave_datos(self, envoltura: bytes) -> bytes:
        """Desenvuelve (descifra) una DEK; el KEK permanece en el HSM o KMS."""
        ...
