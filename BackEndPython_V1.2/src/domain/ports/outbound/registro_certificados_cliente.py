from __future__ import annotations

from typing import Protocol

from src.domain.value_objects.identidad_certificado import IdentidadCertificado
from src.domain.value_objects.principal_certificado import PrincipalCertificado


class RegistroCertificadosCliente(Protocol):
    """AP-0003: allow-list que resuelve un certificado de cliente a su principal.

    Puerto de salida (PEP 544, subtipado estructural). Dada la identidad X.509
    validada por el edge, devuelve el PrincipalCertificado asociado, o None si la
    huella no esta registrada (certificado desconocido, acceso denegado). El
    adaptador de infraestructura la implementa desde configuracion, base de datos
    o KMS, sin que el dominio conozca la fuente.
    """

    def resolver(self, identidad: IdentidadCertificado) -> PrincipalCertificado | None: ...
