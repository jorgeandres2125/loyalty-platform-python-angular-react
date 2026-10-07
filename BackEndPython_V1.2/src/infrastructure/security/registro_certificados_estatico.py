from __future__ import annotations

from src.domain.value_objects.identidad_certificado import IdentidadCertificado
from src.domain.value_objects.principal_certificado import PrincipalCertificado


class RegistroCertificadosEstatico:
    """AP-0003: allow-list de certificados de cliente cargada desde configuracion.

    Implementa el puerto RegistroCertificadosCliente (por forma, PEP 544). El mapa
    asocia la huella SHA-256 normalizada (minusculas, sin dos puntos) de cada
    certificado autorizado con su PrincipalCertificado. En staging y produccion el
    origen del mapa es un secreto inyectado (Key Vault o KMS), nunca el codigo.
    """

    def __init__(self, por_fingerprint: dict[str, PrincipalCertificado]) -> None:
        self._por_fingerprint: dict[str, PrincipalCertificado] = {
            huella.replace(":", "").strip().lower(): principal
            for huella, principal in por_fingerprint.items()
        }

    def resolver(self, identidad: IdentidadCertificado) -> PrincipalCertificado | None:
        return self._por_fingerprint.get(identidad.fingerprint)

    @classmethod
    def desde_config(cls, crudo: str) -> RegistroCertificadosEstatico:
        """Construye el registro desde el formato de configuracion
        "fingerprint|sistema|empresa;fingerprint|sistema|empresa".

        Entradas mal formadas se ignoran (fail-closed: no se registra un
        certificado que no se pueda interpretar por completo).
        """
        por_fingerprint: dict[str, PrincipalCertificado] = {}
        for entrada in crudo.split(";"):
            partes: list[str] = [parte.strip() for parte in entrada.split("|")]
            if len(partes) != 3 or not partes[0] or not partes[1]:
                continue
            huella, sistema, empresa = partes
            por_fingerprint[huella.replace(":", "").lower()] = PrincipalCertificado(
                sistema=sistema, empresa=empresa, activo=True
            )
        return cls(por_fingerprint)
